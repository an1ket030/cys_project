// main.js - Modern JS Logic for PSI Pro GUI

// --- View Router ---
function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    event.currentTarget.classList.add('active');
    document.getElementById(tabId).classList.add('active');
}

function switchThreat(index, element) {
    document.querySelectorAll('.threat-list li').forEach(li => li.classList.remove('active'));
    document.querySelectorAll('.threat-scenario').forEach(s => {
        s.classList.remove('active', 'animate-fade-in-up');
        s.classList.add('d-none');
    });

    element.classList.add('active');
    const target = document.getElementById(`scenario-${index}`);
    target.classList.remove('d-none');
    target.classList.add('animate-fade-in-up', 'active');
}

// --- Utils ---
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function logLine(elId, msg, type = "gen") {
    const el = document.getElementById(elId);
    el.classList.remove('d-none');
    const time = new Date().toISOString().split('T')[1].substring(0, 8);
    let cssClass = "";
    if (type === 'suc') cssClass = "log-suc";
    if (type === 'err') cssClass = "log-err";
    if (type === 'wrn') cssClass = "log-wrn";

    el.innerHTML += `<div class="${cssClass}">[${time}] ${msg}</div>`;
    el.scrollTop = el.scrollHeight;
}

function renderList(containerId, title, items, isAlice = true) {
    const el = document.getElementById(containerId);
    let html = `<div class="section-title">${title} <span style="opacity: 0.5; font-size: 0.75rem;">(${items.length} preview)</span></div>`;
    items.forEach(i => {
        let display = i;
        // Truncate hex hashes for aesthetics
        if (typeof i === 'string' && i.length > 30) {
            display = i.substring(0, 12) + '...' + i.substring(i.length - 8);
        }
        html += `<div class="item">${display}</div>`;
    });
    el.innerHTML = html;

    // Update state label
    const stateEl = document.getElementById(isAlice ? 'alice-state' : 'bob-state');
    stateEl.innerText = title;
}

/* =========================================================
   PROTOCOL LOGIC & ANIMATIONS
========================================================= */

// Packet Animator
function firePackets(direction, count, color = "var(--purple-500)") {
    const layer = document.getElementById('packet-layer');
    for (let i = 0; i < count; i++) {
        setTimeout(() => {
            const p = document.createElement('div');
            p.style.position = 'absolute';
            p.style.width = '10px'; p.style.height = '10px';
            p.style.background = color; p.style.borderRadius = '50%'; p.style.boxShadow = `0 0 10px ${color}`;
            p.style.zIndex = 100; p.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';

            // Hardcoded approx positions for visual flair
            const srcX = direction === 'A2B' ? window.innerWidth * 0.3 : window.innerWidth * 0.7;
            const dstX = direction === 'A2B' ? window.innerWidth * 0.7 : window.innerWidth * 0.3;
            const y = window.innerHeight * 0.6 + (Math.random() * 40 - 20); // jitter

            p.style.left = srcX + 'px';
            p.style.top = y + 'px';
            layer.appendChild(p);

            // Trigger anim
            setTimeout(() => { p.style.left = dstX + 'px'; }, 20);
            setTimeout(() => { p.remove(); }, 450);
        }, i * 40);
    }
}

async function generateDataset() {
    const size = document.getElementById('ds-size').value;
    const overlap = document.getElementById('ds-overlap').value;
    const btn = document.getElementById('btn-generate');
    btn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Generating...';
    btn.disabled = true;

    try {
        const res = await fetch('/api/setup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ size: parseInt(size), overlap: parseInt(overlap) })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        document.getElementById('setup-logs').innerHTML = '';
        logLine('setup-logs', `System Initialized. Alice Size: ${data.alice_size}, Bob Size: ${data.bob_size}`, 'suc');
        logLine('setup-logs', "Intersection Overlap hidden. Mathematical parameters locked.");

        renderList('alice-list', 'Raw Contacts Database', data.alice_sample, true);
        renderList('bob-list', 'Raw Contacts Database', data.bob_sample, false);

        // Update Pipeline UI
        document.getElementById('btn-hash').disabled = false;
        document.getElementById('btn-mask').disabled = true;
        document.getElementById('btn-double').disabled = true;
        document.getElementById('btn-intersect').disabled = true;
        document.getElementById('intersection-result').classList.add('d-none');

    } catch (err) {
        logLine('setup-logs', err.message, 'err');
    } finally {
        btn.innerHTML = '<i class="ph ph-lightning"></i> Generate Cryptographic State';
        btn.disabled = false;
    }
}

async function stepHash() {
    const btn = document.getElementById('btn-hash');
    btn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Hashing...';
    try {
        const res = await fetch('/api/step/hash', { method: 'POST' });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        await sleep(150); // UI delay 
        renderList('alice-list', 'SHA-256 Hashes', data.alice_hashed_sample, true);
        renderList('bob-list', 'SHA-256 Hashes', data.bob_hashed_sample, false);

        btn.disabled = true; btn.innerHTML = '<i class="ph ph-check"></i> SHA-256 Hash';
        document.getElementById('btn-mask').disabled = false;
    } catch (err) { alert(err.message); btn.innerHTML = 'Error'; }
}

async function stepMask() {
    const btn = document.getElementById('btn-mask');
    btn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Masking...';
    try {
        const res = await fetch('/api/step/mask', { method: 'POST' });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        await sleep(250);
        renderList('alice-list', 'ECC Base Masked H(x)^k_a', data.alice_masked_sample, true);
        renderList('bob-list', 'ECC Base Masked H(x)^k_b', data.bob_masked_sample, false);

        btn.disabled = true; btn.innerHTML = '<i class="ph ph-check"></i> ECC Mask H(x)^k';
        document.getElementById('btn-double').disabled = false;
    } catch (err) { alert(err.message); }
}

async function stepDoubleMask() {
    const btn = document.getElementById('btn-double');
    btn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Exchanging...';

    // VISUAL FEEDBACK
    document.getElementById('alice-list').innerHTML = `<div class="placeholder"><i class="ph ph-arrows-left-right ph-spin" style="font-size:2rem"></i> <br/>Transacting with Network...</div>`;
    document.getElementById('bob-list').innerHTML = `<div class="placeholder"><i class="ph ph-arrows-left-right ph-spin" style="font-size:2rem"></i> <br/>Transacting with Network...</div>`;
    firePackets('A2B', 10);
    firePackets('B2A', 10, "var(--emerald-500)");

    try {
        const res = await fetch('/api/step/double_mask', { method: 'POST' });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        await sleep(500); // wait for packets

        // After exchange, they secondary mask the received data
        renderList('alice-list', 'Remote Data Doubly Masked (k_b^k_a)', data.alice_double_masked_sample, true);
        renderList('bob-list', 'Remote Data Doubly Masked (k_a^k_b)', data.bob_double_masked_sample, false);

        btn.disabled = true; btn.innerHTML = '<i class="ph ph-check"></i> Exchange Complete';
        document.getElementById('btn-intersect').disabled = false;
    } catch (err) { alert(err.message); }
}

async function stepIntersect() {
    const btn = document.getElementById('btn-intersect');
    btn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Securing Intersection...';
    try {
        const res = await fetch('/api/step/intersect', { method: 'POST' });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        await sleep(300);

        // UI Complete
        btn.disabled = true; btn.innerHTML = '<i class="ph ph-check-circle"></i> Computed Successfully';

        const banner = document.getElementById('intersection-result');
        banner.classList.remove('d-none');
        document.getElementById('intersect-count').innerText = data.intersection_size;

        const listDiv = document.getElementById('intersect-samples');
        let html = '';
        data.intersection_sample.forEach(i => { html += `<div><i class="ph ph-user"></i> ${i}</div>`; });
        listDiv.innerHTML = html;

    } catch (err) { alert(err.message); }
}

/* =========================================================
   SECURITY SIMULATORS
========================================================= */

// EAVESDROPPER
async function simEavesdrop() {
    document.getElementById('log-eavesdrop').innerHTML = '';
    logLine('log-eavesdrop', "[SYS] Eavesdropper node injected into wire.", "wrn");

    // Animate stage
    const stage = document.getElementById('stage-eavesdrop');
    const p = document.createElement('div');
    p.className = 'packet'; p.style.left = '30px'; p.style.opacity = '1';
    stage.appendChild(p);

    // move packet to middle
    setTimeout(() => { p.style.left = '50%'; }, 20);

    await sleep(300);
    p.classList.add('intercepted'); // expands on hacker icon
    logLine('log-eavesdrop', "[HACKER] Packet intercepted successfully!");

    try {
        const res = await fetch('/api/attack/eavesdrop');
        const data = await res.json();
        if (data.status === 'error') { logLine('log-eavesdrop', data.message, 'err'); p.remove(); return; }

        logLine('log-eavesdrop', `[HACKER] Dump: ${data.intercepted_hash.substring(0, 20)}...`);
        logLine('log-eavesdrop', "[HACKER] Firing bruteforce inverse discrete log...", "wrn");
        await sleep(500);
        logLine('log-eavesdrop', `[SYSTEM RESULT] ECDLP Infeasible. ${data.explanation}`, "suc");

        setTimeout(() => { p.remove(); }, 300);
    } catch (e) { }
}

// DICTIONARY
async function simDict() {
    document.getElementById('log-dictionary').innerHTML = '';
    logLine('log-dictionary', "[BOB-MALICIOUS] Loading 5000-word dictionary payload...", "err");

    const stage = document.getElementById('stage-dict');
    let packets = [];

    // Fire many red packets right
    for (let i = 0; i < 8; i++) {
        setTimeout(() => {
            const p = document.createElement('div');
            p.className = 'packet malicious'; p.style.right = '70px'; p.style.left = 'auto'; p.style.opacity = '1';
            stage.appendChild(p);
            setTimeout(() => { p.style.right = 'calc(100% - 100px)'; }, 20);
            packets.push(p);
        }, i * 50);
    }

    await sleep(300);
    logLine('log-dictionary', "[ALICE] Incoming connection. Verifying metadata...", "wrn");

    // Shield pops up
    const shield = document.createElement('div');
    shield.className = 'shield-wall';
    stage.appendChild(shield);
    setTimeout(() => shield.style.opacity = '1', 10);
    document.getElementById('alice-shield').style.color = 'var(--emerald-500)';

    await sleep(300);
    packets.forEach(p => Math.random() > 0.5 ? p.style.opacity = 0 : p.classList.add('intercepted')); // crash into shield

    try {
        const res = await fetch('/api/attack/dictionary');
        const data = await res.json();
        logLine('log-dictionary', `[ALICE RESPONSE] ${data.detail}`, "suc");
        setTimeout(() => { packets.forEach(p => p.remove()); shield.remove(); document.getElementById('alice-shield').style.color = ''; }, 500);
    } catch (e) { }
}

// INVALID CURVE
async function simCurve() {
    document.getElementById('log-curve').innerHTML = '';
    logLine('log-curve', "[HACKER] Crafting byte-modified ECC hex format...", "err");
    await sleep(150);
    logLine('log-curve', "[HACKER] Dispatching payload to Node A.");

    const stage = document.getElementById('stage-curve');
    const p = document.createElement('div');
    p.className = 'packet malicious'; p.style.right = '70px'; p.style.left = 'auto'; p.style.opacity = '1';
    p.style.borderRadius = '0'; // looks broken
    stage.appendChild(p);

    // Moves to A
    setTimeout(() => { p.style.right = 'calc(100% - 90px)'; }, 20);
    await sleep(300);

    logLine('log-curve', "[ALICE] Decoding packet points...", "wrn");
    await sleep(150);

    // Rejected visually - bounce back and disappear
    p.style.right = 'calc(100% - 150px)';
    p.style.opacity = '0';
    p.style.background = 'var(--orange-500)';

    try {
        const res = await fetch('/api/attack/invalid_curve');
        const data = await res.json();
        logLine('log-curve', `[ALICE FAULT HANDLER] ${data.detail}`, "suc");
        setTimeout(() => { p.remove(); }, 300);
    } catch (e) { }
}
