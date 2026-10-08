document.documentElement.classList.add('js');
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const api = async (p, o) => { const r = await fetch('/api' + p, o); if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText); return r.json(); };
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const chips = (a, c = '') => a.map(t => `<span class="${c}">${esc(t)}</span>`).join('');
const still = matchMedia('(prefers-reduced-motion:reduce)').matches, fine = matchMedia('(hover:hover) and (pointer:fine)').matches;
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: .1 });
const reveal = () => $$('.reveal:not(.in)').forEach((el, i) => { el.style.setProperty('--d', (i % 4) * .08 + 's'); io.observe(el); });
const LANG = ['#7c5cff', '#a78bfa', '#38bdf8', '#34d399', '#fbbf24', '#f472b6'];

function render(p, sk, pr, ed, ac) {
  document.title = `${p.name} | ${p.title}`;
  $('#name').textContent = p.name; $('#objective').textContent = p.objective; $('#tagline').textContent = p.tagline;
  $('#gh').href = 'https://github.com/' + p.github; $('#mail').href = 'mailto:' + p.email;
  if (p.has_resume) $('#cv').hidden = false;
  const g = {}; sk.forEach(s => (g[s.category] = g[s.category] || []).push(...s.items));
  $('#skills').innerHTML = Object.entries(g).map(([c, it]) => `<div class="cat">${esc(c)}</div><div class="chips">${it.map(i => `<span class="${i.level >= 75 ? 'strong' : ''}">${esc(i.name)}</span>`).join('')}</div>`).join('');
  $('#edu').innerHTML = ed.map(e => `<div class="row"><h4>${esc(e.degree)}</h4><p>${esc(e.institution)} · ${esc(e.period)}</p></div>`).join('');
  $('#ach').innerHTML = ac.map(a => `<div class="row"><h4>${esc(a.icon)} ${esc(a.title)}</h4><p>${esc(a.detail)}</p></div>`).join('');
  $('#proj-grid').innerHTML = pr.map(x => `<article class="card proj reveal"><span class="badge">${esc(x.badge)}</span><h3>${esc(x.title)}</h3>
    <p>${esc(x.description)}</p><div class="chips">${chips(x.tech)}</div><a href="${esc(x.link)}" target="_blank" rel="noopener">View code →</a></article>`).join('');
  $('#contact-list').innerHTML = [['Email', p.email], ['Phone', p.phone], ['GitHub', '@' + p.github], ['Location', p.location]].map(([k, v]) => `<li><b>${k}</b>${esc(v)}</li>`).join('');
  $('#graph').src = `https://ghchart.rshah.org/7c5cff/${p.github}`; $('#graph').onload = e => e.target.hidden = false;
  roles(p.roles);
}

/* GitHub: backend proxy first, direct GitHub API as fallback */
async function loadGithub(user) {
  let d;
  try { d = await api('/github'); } catch {
    try {
      const [u, r] = await Promise.all([`/users/${user}`, `/users/${user}/repos?per_page=100&sort=pushed`].map(u => fetch('https://api.github.com' + u).then(r => r.ok ? r.json() : Promise.reject())));
      const repos = r.filter(x => !x.fork);
      const langs = {}; repos.forEach(x => x.language && (langs[x.language] = (langs[x.language] || 0) + 1));
      d = { user: u, stars: repos.reduce((a, x) => a + x.stargazers_count, 0), languages: Object.entries(langs).sort((a, b) => b[1] - a[1]).slice(0, 6),
        repos: repos.sort((a, b) => b.stargazers_count - a.stargazers_count || b.pushed_at.localeCompare(a.pushed_at)).slice(0, 6) };
    } catch { $('#gh-profile').innerHTML = `<p class="muted">Couldn't load GitHub right now. <a href="https://github.com/${esc(user)}" target="_blank" rel="noopener" style="color:var(--p2)">Visit @${esc(user)} →</a></p>`; return; }
  }
  const u = d.user, tot = d.languages.reduce((a, [, n]) => a + n, 0) || 1;
  $('#gh-profile').innerHTML = `<img src="${esc(u.avatar_url)}" alt="" width="84" height="84"><div style="flex:1;min-width:220px"><h3>${esc(u.name || u.login)} <a href="${esc(u.html_url)}" target="_blank" rel="noopener" style="color:var(--p2);font-size:.9rem">@${esc(u.login)}</a></h3>
    <p class="muted">${esc(u.bio || '')}</p><div class="nums"><div><b>${u.public_repos}</b><small>Repos</small></div><div><b>${d.stars}</b><small>Stars</small></div><div><b>${u.followers}</b><small>Followers</small></div></div></div>
    ${d.languages.length ? `<div class="bar">${d.languages.map(([l, n], i) => `<i style="width:${n / tot * 100}%;background:${LANG[i]}" title="${esc(l)}"></i>`).join('')}</div>
    <div class="legend">${d.languages.map(([l, n], i) => `<span><s style="background:${LANG[i]}"></s>${esc(l)}</span>`).join('')}</div>` : ''}`;
  $('#gh-repos').innerHTML = d.repos.map(r => `<a class="card proj reveal" href="${esc(r.html_url)}" target="_blank" rel="noopener"><h3>${esc(r.name)}</h3>
    <p>${esc(r.description || 'No description yet.')}</p><div class="meta"><span>${esc(r.language || '—')}</span><span>★ ${r.stargazers_count}</span><span>⑂ ${r.forks_count}</span></div></a>`).join('');
  $$('#stats b[data-k]').forEach(b => b.textContent = { repos: u.public_repos, stars: d.stars, followers: u.followers }[b.dataset.k]);
  reveal();
}

function roles(words) {
  const el = $('#role'), split = w => { const a = w.split(' '); return a.length > 1 ? `<b>${esc(a.slice(0, -1).join(' '))}</b>${esc(a.at(-1))}` : esc(w); };
  if (still) return el.innerHTML = split(words[0]);
  let i = 0; (function next() { el.style.transition = 'opacity .4s,transform .4s'; el.style.opacity = 0; el.style.transform = 'translateY(14px)';
    setTimeout(() => { el.innerHTML = split(words[i++ % words.length]); el.style.opacity = 1; el.style.transform = ''; }, 400); setTimeout(next, 2800); })();
}

/* nav, offer accordion, form, motion */
const nav = $('#nav'), links = $('#links'), menu = $('#menu');
addEventListener('scroll', () => { nav.classList.toggle('scrolled', scrollY > 20); const h = document.documentElement; $('#progress').style.transform = `scaleX(${scrollY / (h.scrollHeight - h.clientHeight || 1)})`; }, { passive: true });
menu.onclick = () => menu.setAttribute('aria-expanded', links.classList.toggle('open'));
links.onclick = e => e.target.closest('a') && (links.classList.remove('open'), menu.setAttribute('aria-expanded', false));
const spy = new IntersectionObserver(es => es.forEach(e => e.isIntersecting && $$('a', links).forEach(l => l.classList.toggle('active', l.hash === '#' + e.target.id))), { rootMargin: '-45% 0px -50% 0px' });
$$('main section').forEach(s => spy.observe(s));
$$('.ohead').forEach(b => b.onclick = () => { const c = b.closest('.ocard'), o = c.classList.toggle('open'); b.setAttribute('aria-expanded', o); });
$('#form').addEventListener('submit', async e => {
  e.preventDefault(); const f = e.target, st = $('#form-status'), btn = $('button', f);
  btn.disabled = true; btn.textContent = 'Sending…'; st.className = st.textContent = '';
  try { const r = await api('/contact', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.fromEntries(new FormData(f))) }); st.textContent = r.detail; st.className = 'ok'; f.reset(); }
  catch { st.textContent = 'Could not send. Please check your name, a valid email and a message.'; st.className = 'err'; }
  finally { btn.disabled = false; btn.textContent = 'Send message'; }
});
if (fine && !still) { const g = $('#glow'); let x = 0, y = 0, tx = 0, ty = 0;
  addEventListener('mousemove', e => { tx = e.clientX; ty = e.clientY; g.style.opacity = 1; });
  (function f() { x += (tx - x) * .15; y += (ty - y) * .15; g.style.transform = `translate(${x - 13}px,${y - 13}px)`; requestAnimationFrame(f); })(); }

$('#stats').innerHTML = [['repos', 'Public repos'], ['stars', 'GitHub stars'], ['followers', 'Followers']].map(([k, l]) => `<div><b data-k="${k}">–</b><small>${l}</small></div>`).join('') + '<div><b>1st</b><small>Hackathon 2026</small></div>';
(async () => {
  let p;
  try { const [pp, ...rest] = await Promise.all(['/profile', '/skills', '/projects', '/education', '/achievements'].map(u => api(u))); p = pp; render(pp, ...rest); }
  catch { $('main').insertAdjacentHTML('afterbegin', '<p style="padding:7rem 6vw;color:var(--mut)">Could not reach the API. Start the server with: uvicorn backend.main:app</p>'); }
  reveal(); api('/visit', { method: 'POST' }).then(v => $('#visits').textContent = v.visits + ' visits').catch(() => {});
  loadGithub(p?.github || 'adilkhan107');
})();
