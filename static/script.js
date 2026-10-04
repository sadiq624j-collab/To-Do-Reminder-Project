// The interface calls Python; Python owns and saves the task list.
const $ = id => document.getElementById(id);
let tasks = [], filter = 'all', deleteId = null, busy = false;
$('today').textContent = new Date().toLocaleDateString(undefined, {weekday:'short', month:'short', day:'numeric', year:'numeric'});
function notice(message, error = false) {
  $('notice').textContent = message;
  $('notice').classList.toggle('error', error);
}
function render() {
  const done = tasks.filter(t => t.Done).length;
  $('total').textContent = tasks.length;
  $('sideCount').textContent = tasks.length;
  $('pending').textContent = tasks.length - done;
  $('completed').textContent = done;
  const visible = tasks.filter(t => filter === 'all' || (filter === 'done' ? t.Done : !t.Done));
  $('listCount').textContent = visible.length;
  $('taskList').replaceChildren();
  visible.forEach(task => {
    const row = document.createElement('li');
    row.className = 'task-row' + (task.Done ? ' done' : '');
    const check = document.createElement('button');
    check.className = 'check'; check.textContent = task.Done ? '✓' : '';
    check.setAttribute('aria-label', (task.Done ? 'Mark pending: ' : 'Mark complete: ') + task.task);
    check.setAttribute('aria-pressed', String(task.Done));
    check.onclick = () => mutate('/api/complete', {id:task.id}, task.Done ? 'Task moved to pending.' : 'Nice work! Task completed.');
    const title = document.createElement('span');
    title.className = 'task-title'; title.textContent = task.task;
    const badge = document.createElement('span');
    badge.className = 'badge'; badge.textContent = task.Done ? 'Completed' : 'In progress';
    const remove = document.createElement('button'); remove.className = 'delete';
    remove.setAttribute('aria-label', 'Delete: ' + task.task);
    remove.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 10v7m4-7v7"/></svg>';
    remove.onclick = () => { deleteId = task.id; $('deleteName').textContent = task.task; $('deleteDialog').showModal(); $('cancelDelete').focus(); };
    row.append(check, title, badge, remove); $('taskList').append(row);
  });
  $('empty').hidden = visible.length > 0;
  $('emptyTitle').textContent = filter === 'done' ? 'Your next win is waiting' : filter === 'pending' && tasks.length ? 'All caught up!' : 'A fresh start awaits';
  $('emptyText').textContent = filter === 'done' ? 'Complete a task and it will appear here.' : filter === 'pending' && tasks.length ? 'Every task is complete. Enjoy a little breathing room.' : 'Add your first task above and take the first step.';
  const percent = tasks.length ? Math.round(done / tasks.length * 100) : 0;
  $('progressText').textContent = `${done} of ${tasks.length} tasks completed`;
  $('progressBar').style.width = percent + '%'; $('percent').textContent = percent + '%';
  document.querySelector('.progress-track').setAttribute('aria-valuenow', percent);
}
async function mutate(path, body, message) {
  if (busy) return false;
  busy = true; document.querySelectorAll('button').forEach(b => b.disabled = true);
  try {
    const response = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Unable to update task.');
    tasks = result; render(); notice(message); return true;
  } catch (error) { notice(error.message === 'Failed to fetch' ? 'Cannot reach Python. Make sure app.py is still running, then reload.' : error.message, true); return false;
  } finally { busy = false; document.querySelectorAll('button').forEach(b => b.disabled = false); }
}
$('addForm').onsubmit = async event => {
  event.preventDefault(); const title = $('taskInput').value.trim();
  if (!title) { notice('Please enter a task first.', true); $('taskInput').focus(); return; }
  if (await mutate('/api/tasks', {task:title}, 'Task added to your list.')) {
    $('taskInput').value = ''; $('taskInput').focus();
  }
};
document.querySelectorAll('[data-filter]').forEach(button => button.onclick = () => {
  filter = button.dataset.filter;
  document.querySelectorAll('[data-filter]').forEach(b => { b.classList.toggle('selected', b === button); b.setAttribute('aria-pressed', String(b === button)); }); render();
});
$('cancelDelete').onclick = () => $('deleteDialog').close();
$('confirmDelete').onclick = async () => { if (await mutate('/api/delete', {id:deleteId}, 'Task deleted.')) $('deleteDialog').close(); };
(async () => {
  try {
    const response = await fetch('/api/tasks');
    if (!response.ok) throw new Error();
    tasks = await response.json(); render();
  } catch { notice('Could not load tasks. Keep app.py running and reload this page.', true); }
})();
