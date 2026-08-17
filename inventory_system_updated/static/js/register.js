function checkStrength(val) {
    const fill = document.getElementById('strengthFill');
    const label = document.getElementById('strengthLabel');
    let score = 0;
    if (val.length >= 8) score++;
    if (/[A-Z]/.test(val)) score++;
    if (/[0-9]/.test(val)) score++;
    if (/[^A-Za-z0-9]/.test(val)) score++;
    const levels = [
    { w: '0%',   c: 'transparent', t: '' },
    { w: '25%',  c: '#e05555', t: 'Weak' },
    { w: '50%',  c: '#e0913a', t: 'Fair' },
    { w: '75%',  c: '#4f8ef7', t: 'Good' },
    { w: '100%', c: '#4caf7d', t: 'Strong' },
    ];
    const lvl = val.length === 0 ? levels[0] : levels[score] || levels[1];
    fill.style.width = lvl.w;
    fill.style.background = lvl.c;
    label.textContent = lvl.t;
    label.style.color = lvl.c;
}