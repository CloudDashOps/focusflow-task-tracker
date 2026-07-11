import { useEffect, useMemo, useState } from 'react';
import { createTask, deleteTask, fetchTasks, updateTask } from './api';
import './App.css';

const blankTask = { title: '', category: 'General', priority: 'medium', due_date: '' };
const categories = ['General', 'Work', 'Personal', 'Study', 'Health'];

function toApiTask(task) {
  return { ...task, due_date: task.due_date ? new Date(`${task.due_date}T12:00:00`).toISOString() : null };
}

function App() {
  const [tasks, setTasks] = useState([]);
  const [form, setForm] = useState(blankTask);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => { loadTasks(); }, []);

  async function loadTasks() {
    try { setLoading(true); setTasks(await fetchTasks()); }
    catch { setError('Could not connect to the API. Make sure the backend is running.'); }
    finally { setLoading(false); }
  }

  const visibleTasks = useMemo(() => tasks.filter((task) => {
    const matchesSearch = task.title.toLowerCase().includes(search.toLowerCase()) || task.category.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || (filter === 'active' && !task.completed) || (filter === 'completed' && task.completed) || task.priority === filter;
    return matchesSearch && matchesFilter;
  }), [tasks, filter, search]);

  const completed = tasks.filter((task) => task.completed).length;
  const progress = tasks.length ? Math.round((completed / tasks.length) * 100) : 0;

  async function handleSubmit(event) {
    event.preventDefault();
    if (!form.title.trim()) return setError('Give your task a title first.');
    try {
      setError('');
      if (editingId) {
        const updated = await updateTask(editingId, toApiTask(form));
        setTasks(tasks.map((task) => task.id === editingId ? updated : task));
      } else {
        const created = await createTask(toApiTask(form));
        setTasks((current) => [created, ...current]);
      }
      setForm(blankTask); setEditingId(null);
    } catch { setError('Your task could not be saved. Please try again.'); }
  }

  async function toggleTask(task) {
    try {
      const updated = await updateTask(task.id, { completed: !task.completed });
      setTasks(tasks.map((item) => item.id === task.id ? updated : item));
    } catch { setError('Could not update that task.'); }
  }

  async function removeTask(id) {
    try { await deleteTask(id); setTasks(tasks.filter((task) => task.id !== id)); }
    catch { setError('Could not delete that task.'); }
  }

  function beginEdit(task) {
    setEditingId(task.id);
    setForm({ title: task.title, category: task.category || 'General', priority: task.priority || 'medium', due_date: task.due_date ? task.due_date.slice(0, 10) : '' });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  async function clearCompleted() {
    try {
      await Promise.all(tasks.filter((task) => task.completed).map((task) => deleteTask(task.id)));
      setTasks(tasks.filter((task) => !task.completed));
    } catch { setError('Could not clear completed tasks.'); }
  }

  return <main className="page-shell">
    <section className="dashboard">
      <header className="hero">
        <div><p className="eyebrow">PERSONAL PRODUCTIVITY</p><h1>FocusFlow</h1><p className="subtitle">Turn today’s plans into meaningful progress.</p></div>
        <div className="date-badge"><span>{new Intl.DateTimeFormat('en-US', { weekday: 'long' }).format(new Date())}</span><strong>{new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(new Date())}</strong></div>
      </header>

      <section className="summary-grid">
        <div className="progress-card"><div><p>Today’s progress</p><strong>{progress}%</strong></div><div className="progress-ring" style={{ '--progress': `${progress * 3.6}deg` }}><span>{completed}/{tasks.length || 0}</span></div><div className="progress-track"><i style={{ width: `${progress}%` }} /></div></div>
        <div className="stat-card"><span className="stat-icon violet">✓</span><div><strong>{completed}</strong><p>Completed</p></div></div>
        <div className="stat-card"><span className="stat-icon orange">⌁</span><div><strong>{tasks.length - completed}</strong><p>To focus on</p></div></div>
      </section>

      <section className="panel composer">
        <div className="panel-heading"><div><h2>{editingId ? 'Edit task' : 'Create a task'}</h2><p>{editingId ? 'Update the details below.' : 'A clear next step makes it easier to begin.'}</p></div>{editingId && <button className="text-button" onClick={() => { setEditingId(null); setForm(blankTask); }}>Cancel edit</button>}</div>
        <form onSubmit={handleSubmit}>
          <input className="title-input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="What needs to be done?" maxLength="255" autoFocus />
          <div className="form-row"><label>Category<select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>{categories.map((category) => <option key={category}>{category}</option>)}</select></label><label>Priority<select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option></select></label><label>Due date<input type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} /></label><button className="primary-button" type="submit">{editingId ? 'Save changes' : '+ Add task'}</button></div>
        </form>
      </section>

      <section className="panel tasks-panel">
        <div className="tasks-toolbar"><div><h2>Your tasks</h2><p>{tasks.length ? `${tasks.length - completed} task${tasks.length - completed === 1 ? '' : 's'} remaining` : 'Your list is ready when you are.'}</p></div><div className="toolbar-actions"><input aria-label="Search tasks" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search tasks" /><button className="text-button" onClick={clearCompleted} disabled={!completed}>Clear completed</button></div></div>
        <div className="filters">{[['all', 'All'], ['active', 'Active'], ['completed', 'Done'], ['high', 'High priority']].map(([value, label]) => <button className={filter === value ? 'filter active' : 'filter'} key={value} onClick={() => setFilter(value)}>{label}</button>)}</div>
        {error && <div className="error-message">{error}<button onClick={() => setError('')} aria-label="Dismiss error">×</button></div>}
        {loading ? <div className="empty-state">Loading your tasks…</div> : visibleTasks.length ? <ul className="task-list">{visibleTasks.map((task) => <li className={`task-item ${task.completed ? 'done' : ''}`} key={task.id}><button className="check-button" onClick={() => toggleTask(task)} aria-label={`Mark ${task.title} as ${task.completed ? 'active' : 'complete'}`}>{task.completed && '✓'}</button><div className="task-copy"><h3>{task.title}</h3><div className="task-meta"><span>{task.category}</span>{task.due_date && <span className="due-date">Due {new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(new Date(task.due_date))}</span>}</div></div><span className={`priority ${task.priority}`}>{task.priority}</span><div className="task-actions"><button onClick={() => beginEdit(task)}>Edit</button><button className="delete" onClick={() => removeTask(task.id)}>Delete</button></div></li>)}</ul> : <div className="empty-state"><span>✦</span><h3>No tasks found</h3><p>{search || filter !== 'all' ? 'Try a different filter or search term.' : 'Add your first task and get the day moving.'}</p></div>}
      </section>
    </section>
  </main>;
}

export default App;
