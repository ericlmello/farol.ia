(function () {
  const statusEl = document.getElementById('status');
  const audioEl = document.getElementById('remoteAudio');
  const transcriptsEl = document.getElementById('transcripts');
  const CLIENT_ID = window.FAROL_CLIENT_ID || 'unknown';

  function setStatus(text) { if (statusEl) statusEl.textContent = text; }
  async function postLog(type, message, data) {
    try {
      await fetch('/logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: CLIENT_ID, type, message, data })
      });
    } catch (_) { /* ignore */ }
  }
  function appendTranscript(prefix, text) {
    if (!transcriptsEl) return;
    const line = `[${prefix}] ${text}`;
    transcriptsEl.textContent = transcriptsEl.textContent ? (transcriptsEl.textContent + "\n" + line) : line;
  }

  async function ensureAudioPlayback(prime = false) {
    if (!audioEl) return;
    try {
      if (prime) {
        try {
          // Create a silent stream to prime autoplay
          const Ctx = window.AudioContext || window.webkitAudioContext;
          if (Ctx) {
            const ctx = new Ctx();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            const dest = ctx.createMediaStreamDestination();
            gain.gain.value = 0.0; // silence
            osc.connect(gain);
            gain.connect(dest);
            osc.start();
            audioEl.srcObject = dest.stream;
            window._farolPrime = { ctx, osc, gain, dest };
          }
        } catch (e) {
          // ignore priming failure
        }
      }
      await audioEl.play();
    }
    catch (err) {
      // Wait for a user gesture if necessary
      const tryPlayOnce = async () => {
        try { await audioEl.play(); }
        catch (_) { /* ignore */ }
        finally {
          window.removeEventListener('pointerdown', tryPlayOnce);
          window.removeEventListener('keydown', tryPlayOnce);
        }
      };
      window.addEventListener('pointerdown', tryPlayOnce, { once: true });
      window.addEventListener('keydown', tryPlayOnce, { once: true });
    }
  }

  function setupLocalSpeakingDetector(stream) {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const src = ctx.createMediaStreamSource(stream);
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 2048; src.connect(analyser);
      const data = new Uint8Array(analyser.fftSize); let lastAbove = 0; const SILENCE_WINDOW = 600;
      function tick() {
        analyser.getByteTimeDomainData(data);
        let sum = 0; for (let i=0; i<data.length; i++) { const v=(data[i]-128)/128; sum += v*v; }
        const rms = Math.sqrt(sum / data.length); const now = performance.now();
        if (rms > 0.05) { lastAbove = now; setStatus('Falando…'); }
        else if (now - lastAbove > SILENCE_WINDOW) { setStatus('Silêncio detectado… respondendo…'); }
        requestAnimationFrame(tick);
      }
      tick();
    } catch (e) { /* ignore */ }
  }

  function waitForIceGatheringComplete(pc) {
    if (pc.iceGatheringState === 'complete') return Promise.resolve();
    return new Promise((resolve) => {
      function check() {
        if (pc.iceGatheringState === 'complete') {
          pc.removeEventListener('icegatheringstatechange', check);
          resolve();
        }
      }
      pc.addEventListener('icegatheringstatechange', check);
      setTimeout(() => { pc.removeEventListener('icegatheringstatechange', check); resolve(); }, 2500);
    });
  }

  async function main() {
    try {
      setStatus('Aguardando permissão do microfone…');
      await postLog('page_load', 'loaded');
      const mic = await navigator.mediaDevices.getUserMedia({ audio: true });
      await postLog('mic', 'granted');
      audioEl.muted = true; // Avoid feedback if any local playback
      // Prime autoplay right after getUserMedia for stricter browsers
      await ensureAudioPlayback(true);
      setStatus('Microfone ativo. Criando sessão…');

      setupLocalSpeakingDetector(mic);

      const sessResp = await fetch('/session', { method: 'POST' });
      if (!sessResp.ok) {
        const t = await sessResp.text();
        await postLog('session_error', 'failed_create_session', { status: sessResp.status, body: t.substring(0, 500) });
        throw new Error('Falha ao criar sessão: ' + t);
      }
      const session = await sessResp.json();
      const token = (session && session.client_secret && (session.client_secret.value || session.client_secret)) || null;
      if (!token) throw new Error('Token efêmero ausente na resposta do backend.');
      await postLog('session_ok', 'created', { has_token: !!token });

      const pc = new RTCPeerConnection({
        bundlePolicy: 'max-bundle', rtcpMuxPolicy: 'require',
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
      });

      // Optional DataChannel for logs/events
      const dc = pc.createDataChannel('oai-events');
      dc.onopen = () => { console.log('[Farol] DataChannel aberto'); postLog('dc', 'open'); };
      dc.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          // Heuristics for transcripts and assistant messages
          const type = msg.type || '';
          if (/transcript|input|user/.test(type)) {
            const t = msg.text || msg.transcript || msg.content || msg.delta || JSON.stringify(msg);
            if (t) { appendTranscript('Você', String(t)); postLog('transcript_user', 'recv', { t: String(t).slice(0, 500) }); }
          } else if (/response|assistant|output/.test(type)) {
            const t = msg.text || msg.transcript || msg.content || msg.delta || JSON.stringify(msg);
            if (t) { appendTranscript('Farol', String(t)); postLog('transcript_assistant', 'recv', { t: String(t).slice(0, 500) }); }
          } else {
            postLog('dc_event', 'recv', { type, len: ev.data ? ev.data.length : 0 });
          }
        } catch (_) {
          postLog('dc_raw', 'recv', { sample: String(ev.data).slice(0, 120) });
        }
      };

      // Remote audio
      const remoteStream = new MediaStream();
      audioEl.srcObject = remoteStream;
      pc.ontrack = (event) => {
        for (const track of event.streams[0].getTracks()) remoteStream.addTrack(track);
        // Switch from primed silent stream to the remote stream
        try { audioEl.srcObject = remoteStream; } catch (_) {}
        audioEl.muted = false;
        ensureAudioPlayback();
        postLog('media', 'remote_track');
      };

      pc.onconnectionstatechange = () => { setStatus('Estado de conexão: ' + pc.connectionState); postLog('pc', 'state', { state: pc.connectionState }); };
      pc.oniceconnectionstatechange = () => { console.log('[Farol] ICE:', pc.iceConnectionState); postLog('ice', 'state', { state: pc.iceConnectionState }); };

      // Receive audio from model
      try { pc.addTransceiver('audio', { direction: 'recvonly' }); } catch {}
      // Send mic
      mic.getTracks().forEach(t => pc.addTrack(t, mic));

      const offer = await pc.createOffer({ offerToReceiveAudio: true });
      await postLog('rtc', 'offer_created');
      await pc.setLocalDescription(offer);
      await postLog('rtc', 'local_description_set');
      await waitForIceGatheringComplete(pc);

      setStatus('Conectando ao modelo…');
      const sdpResp = await fetch('https://api.openai.com/v1/realtime?model=' + encodeURIComponent(window.FAROL_MODEL || 'gpt-realtime-2025-08-28'), {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer ' + token,
          'Content-Type': 'application/sdp',
          'Accept': 'application/sdp',
          'OpenAI-Beta': 'realtime=v1'
        },
        body: offer.sdp
      });
      if (!sdpResp.ok) {
        const t = await sdpResp.text();
        await postLog('sdp_error', 'answer_failed', { status: sdpResp.status, body: t.substring(0, 500) });
        throw new Error('Falha SDP: ' + t);
      }
      const answer = await sdpResp.text();
      await pc.setRemoteDescription({ type: 'answer', sdp: answer });
      setStatus('Conectado. Fale comigo.');
      await postLog('connected', 'rtc_established');

      window.addEventListener('beforeunload', () => pc.close());
    } catch (err) {
      console.error(err);
      setStatus('Erro: ' + (err && err.message ? err.message : String(err)));
      await postLog('error', 'exception', { message: err && err.message ? err.message : String(err) });
    }
  }

  if (document.readyState === 'complete' || document.readyState === 'interactive') main();
  else window.addEventListener('DOMContentLoaded', main);
})();
