'use strict';

(() => {
  /** DOM helpers **/
  const $ = (id) => document.getElementById(id);

  /** Estado **/
  const threats = [];
  let threatCount = 0;
  let blockedIPs = 0;
  let scansCount = 0;
  let emergency = false;

  /** Utilidades seguras **/
  const rand = (maxExclusive) => Math.floor(Math.random() * maxExclusive);

  function randomIP() {
    // Gera IP “público” (simulado), evitando faixas privadas comuns
    while (true) {
      const a = rand(256), b = rand(256), c = rand(256), d = rand(256);
      const ip = `${a}.${b}.${c}.${d}`;

      // Evita ranges privados e loopback
      if (a === 10) continue;
      if (a === 127) continue;
      if (a === 192 && b === 168) continue;
      if (a === 172 && b >= 16 && b <= 31) continue;

      return ip;
    }
  }

  function token(len = 16) {
    // Token de “integridade” (visual), sem prometer criptografia real
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let out = '';
    for (let i = 0; i < len; i++) out += chars[rand(chars.length)];
    return out;
  }

  function setText(el, value) {
    el.textContent = String(value);
  }

  /** Log (DOM API only, zero innerHTML) **/
  function addLog(message, isDanger = false) {
    const log = $('activityLog');

    const item = document.createElement('div');
    item.className = `log-item${isDanger ? ' danger' : ''}`;

    const time = document.createElement('div');
    time.className = 'log-time';
    setText(time, new Date().toLocaleString('pt-BR'));

    const msg = document.createElement('div');
    msg.className = 'log-message';
    setText(msg, message);

    const status = document.createElement('div');
    status.className = 'log-status';
    setText(status, `SEC-${token(8)} | IP: ${randomIP()}`);

    item.append(time, msg, status);
    log.insertBefore(item, log.firstChild);

    while (log.children.length > 15) {
      log.removeChild(log.lastChild);
    }
  }

  /** Status badge **/
  function flashThreatBadge() {
    const badge = $('statusBadge');

    setText(badge, '● AMEAÇA DETECTADA');
    badge.style.borderColor = '#ff4444';
    badge.style.color = '#ff4444';

    window.setTimeout(() => {
      setText(badge, '● SISTEMA PROTEGIDO');
      badge.style.borderColor = '#00ff88';
      badge.style.color = '#00ff88';
    }, 2500);
  }

  /** Proteções **/
  function toggleSwitch(sw) {
    if (emergency) {
      window.alert('Sistema em modo de emergência: alterações bloqueadas.');
      return;
    }

    sw.classList.toggle('active');
    const active = sw.classList.contains('active');
    sw.setAttribute('aria-checked', active ? 'true' : 'false');

    const name = sw.getAttribute('data-protection') || 'Proteção';
    addLog(`${name} ${active ? 'ATIVADO' : 'DESATIVADO'}`, !active);
  }

  /** Threats **/
  function addThreat(type, severity) {
    if (emergency) return;

    const countries = ['Rússia', 'China', 'EUA', 'Brasil', 'Índia', 'Irã', 'Nigéria', 'Turquia', 'Ucrânia'];
    const t = {
      id: (crypto && crypto.randomUUID) ? crypto.randomUUID() : `${Date.now()}-${rand(1e6)}`,
      type: String(type),
      ip: randomIP(),
      port: [22, 80, 443, 3306, 8080, 21, 25, 3389][rand(8)],
      country: countries[rand(countries.length)],
      time: new Date(),
      severity: String(severity),
      protocol: rand(2) === 0 ? 'TCP' : 'UDP',
      sig: token(12)
    };

    threats.unshift(t);
    threatCount++;
    blockedIPs++;

    setText($('threatCount'), threatCount);
    setText($('blockedIPs'), blockedIPs);
    setText($('totalThreats'), threats.length);
    setText($('todayThreats'), threatCount);

    addLog(`⚠️ ${t.type} NEUTRALIZADO`, true);
    flashThreatBadge();
  }

  /** Modal builder (sem innerHTML) **/
  function buildRow(label, value, cls = 'detail-value', styleText = '') {
    const row = document.createElement('div');
    row.className = 'detail-row';

    const l = document.createElement('span');
    l.className = 'detail-label';
    setText(l, label);

    const v = document.createElement('span');
    v.className = cls;
    setText(v, value);
    if (styleText) v.style.cssText = styleText;

    row.append(l, v);
    return row;
  }

  function buildThreatItem(t) {
    const wrap = document.createElement('div');
    wrap.className = 'threat-item';

    const header = document.createElement('div');
    header.className = 'threat-header';

    const left = document.createElement('div');

    const sev = document.createElement('span');
    sev.className = 'severity';
    setText(sev, t.severity);

    const type = document.createElement('div');
    type.className = 'threat-type';
    setText(type, t.type);

    left.append(sev, type);

    const time = document.createElement('div');
    time.className = 'threat-time';
    setText(time, t.time.toLocaleString('pt-BR'));

    header.append(left, time);

    const details = document.createElement('div');
    details.className = 'threat-details';

    details.append(
      buildRow('🌐 IP ORIGEM:', t.ip, 'detail-value ip'),
      buildRow('🔌 PORTA:', t.port, 'detail-value port'),
      buildRow('📍 ORIGEM:', t.country, 'detail-value', 'color:#ff6b6b;'),
      buildRow('📝 PROTOCOLO:', t.protocol),
      buildRow('🔐 ASSINATURA:', `${t.sig}...`, 'detail-value', 'font-size:11px;')
    );

    wrap.append(header, details);
    return wrap;
  }

  function openModal() {
    if (emergency) {
      window.alert('Sistema bloqueado (modo de emergência).');
      return;
    }

    const modal = $('threatsModal');
    const list = $('threatsList');

    // Limpeza segura
    list.replaceChildren();

    if (threats.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'empty-state';

      const icon = document.createElement('div');
      icon.className = 'empty-icon';
      setText(icon, '🛡️');

      const h3 = document.createElement('h3');
      setText(h3, 'NENHUMA AMEAÇA DETECTADA');

      const p = document.createElement('p');
      setText(p, 'Sistema operando dentro dos parâmetros normais.');

      empty.append(icon, h3, p);
      list.appendChild(empty);
    } else {
      for (const t of threats) list.appendChild(buildThreatItem(t));
    }

    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
  }

  function closeModal() {
    const modal = $('threatsModal');
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
  }

  /** Emergência **/
  function triggerPanic() {
    const ok = window.confirm(
      '🚨 ATIVAR MODO DE EMERGÊNCIA?\n\nA interface será travada até você confirmar o desbloqueio.'
    );
    if (!ok) return;

    emergency = true;
    document.body.style.filter = 'grayscale(100%) brightness(0.55)';
    addLog('🚨 MODO EMERGÊNCIA ATIVADO - INTERFACE BLOQUEADA', true);

    document.querySelectorAll('.switch').forEach((s) => {
      s.style.opacity = '0.5';
      s.style.pointerEvents = 'none';
    });

    // “desbloqueio” simples (demo). Sem prometer segurança real.
    const code = window.prompt('Digite o código de desbloqueio (demo: 2024):');
    if (code === '2024') {
      emergency = false;
      document.body.style.filter = 'none';
      document.querySelectorAll('.switch').forEach((s) => {
        s.style.opacity = '1';
        s.style.pointerEvents = 'auto';
      });
      addLog('✅ Sistema restaurado pelo administrador');
    } else {
      window.alert('Código incorreto. Sistema permanece bloqueado.');
      addLog('❌ Tentativa de desbloqueio falha', true);
    }
  }

  /** Eventos seguros **/
  function clickOrEnterSpace(el, fn) {
    el.addEventListener('click', fn);
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        fn();
      }
    });
  }

  /** Init **/
  setText($('initialTime'), new Date().toLocaleString('pt-BR'));

  addLog('Sistema inicializado');
  addLog('Políticas ativas: CSP forte (sem inline)');
  addLog('Monitoramento carregado com sucesso');

  // Integridade visual (não é “anti-tamper” real, mas sem enganar)
  window.setInterval(() => {
    setText($('tamperCheck'), `INTEGRIDADE: OK · ${token(10)}`);
  }, 2500);

  // Modal
  clickOrEnterSpace($('threatCounter'), openModal);
  $('closeModalBtn').addEventListener('click', closeModal);
  $('threatsModal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeModal();
  });

  // Panic
  $('panicBtn').addEventListener('click', triggerPanic);

  // Switches
  document.querySelectorAll('.switch').forEach((sw) => {
    clickOrEnterSpace(sw, () => toggleSwitch(sw));
  });

  // Simulação de ameaças
  window.setInterval(() => {
    if (emergency) return;

    scansCount++;
    setText($('scansCount'), scansCount);

    if (Math.random() < 0.15) {
      const types = [
        { name: 'Ataque SSH', sev: 'CRÍTICO' },
        { name: 'SQL Injection', sev: 'CRÍTICO' },
        { name: 'Força Bruta', sev: 'ALTO' },
        { name: 'Scan de Portas', sev: 'MÉDIO' },
        { name: 'DDoS Attempt', sev: 'CRÍTICO' }
      ];
      const pick = types[rand(types.length)];
      addThreat(pick.name, pick.sev);
    }
  }, 3500);
})();