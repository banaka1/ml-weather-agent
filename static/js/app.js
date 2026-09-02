const box = document.getElementById('box');
const inp = document.getElementById('inp');
const btn = document.getElementById('btn');

function add(role, text) {
    const d = document.createElement('div');
    d.className = 'm ' + role;
    const av = role === 'ai' ? '🤖' : '👤';
    d.innerHTML = `<div class="av">${av}</div><div class="b">${text}</div>`;
    box.appendChild(d);
    box.scrollTop = box.scrollHeight;
}

function loading() {
    const d = document.createElement('div');
    d.className = 'm ai load';
    d.innerHTML = `<div class="av">🤖</div><div class="b"><span></span><span></span><span></span></div>`;
    box.appendChild(d);
    box.scrollTop = box.scrollHeight;
    return d;
}

async function send() {
    const t = inp.value.trim();
    if (!t) return;
    inp.value = '';
    btn.disabled = true;
    add('me', t);
    const l = loading();
    try {
        const r = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: t })
        });
        const d = await r.json();
        l.remove();
        add('ai', d.reply || d.detail || '无响应');
    } catch (e) {
        l.remove();
        add('ai', '请求失败：' + e.message);
    }
    btn.disabled = false;
    inp.focus();
}

btn.addEventListener('click', send);
inp.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });

document.getElementById('newBtn').addEventListener('click', () => {
    box.innerHTML = '';
    document.querySelector('.side-list li.active')?.classList.remove('active');
    document.querySelector('.side-list li').classList.add('active');
});
