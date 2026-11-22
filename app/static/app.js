document.addEventListener('click', async (event) => {
  const control = event.target.closest('[data-copy]');
  if (!control) return;
  const status = control.parentElement.querySelector('.copy-status');
  try {
    await navigator.clipboard.writeText(control.dataset.copy);
    status.textContent = document.documentElement.lang === 'it' ? 'Copiato' : 'Copied';
  } catch {
    status.textContent = document.documentElement.lang === 'it' ? 'Impossibile copiare' : 'Could not copy';
  }
});