import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import projectService from '../services/projectService';
import authService from '../services/authService';
import Header from '../components/common/Header';
import PDFViewer from '../components/common/PDFViewer';
import '../styles/Dashboard.css';

function ProjectDashboard() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedManual, setSelectedManual] = useState(null);
  const [showShareModal, setShowShareModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [sharedEmployees, setSharedEmployees] = useState([]);
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [currentUser, setCurrentUser] = useState(null);
  const [openMenuId, setOpenMenuId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadProjects();
    loadCurrentUserData();
  }, []);

  useEffect(() => {
    // Close dropdown when clicking outside
    const handleClickOutside = () => setOpenMenuId(null);
    if (openMenuId !== null) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [openMenuId]);

  const loadCurrentUserData = async () => {
    try {
      const user = await authService.getCurrentUser();
      setCurrentUser(user);
    } catch (error) {
      console.error('Failed to load user:', error);
    }
  };

  const loadProjects = async () => {
    try {
      const data = await projectService.listProjects();
      setProjects(data);
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadEmployees = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/employees/list', {
        headers: {
          'Authorization': `Bearer ${authService.getToken()}`
        }
      });
      
      console.log('Employees API response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Loaded employees:', data);
        setEmployees(data);
      } else {
        const errorText = await response.text();
        console.error('Failed to load employees:', response.status, errorText);
      }
    } catch (error) {
      console.error('Failed to load employees:', error);
    }
  };

  const loadProjectShares = async (projectId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/projects/${projectId}/shares`, {
        headers: {
          'Authorization': `Bearer ${authService.getToken()}`
        }
      });
      const data = await response.json();
      setSharedEmployees(data);
    } catch (error) {
      console.error('Failed to load project shares:', error);
    }
  };

  const handleShareClick = async (project) => {
    setSelectedProject(project);
    console.log('Opening share dialog for project:', project.id);
    await loadEmployees();
    await loadProjectShares(project.id);
    console.log('Employees state:', employees);
    console.log('Shared employees state:', sharedEmployees);
    setShowShareModal(true);
    setOpenMenuId(null);
  };

  const handleShareProject = async (employeeId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/projects/${selectedProject.id}/share`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authService.getToken()}`
        },
        body: JSON.stringify({ user_id: employeeId })
      });

      if (response.ok) {
        await loadProjectShares(selectedProject.id);
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to share project');
      }
    } catch (error) {
      console.error('Failed to share project:', error);
      alert('Failed to share project');
    }
  };

  const handleUnshareProject = async (employeeId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/projects/${selectedProject.id}/share/${employeeId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authService.getToken()}`
        }
      });

      if (response.ok) {
        await loadProjectShares(selectedProject.id);
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to unshare project');
      }
    } catch (error) {
      console.error('Failed to unshare project:', error);
      alert('Failed to unshare project');
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      await projectService.createProject(projectName, projectDescription);
      setShowCreateModal(false);
      setProjectName('');
      setProjectDescription('');
      loadProjects();
    } catch (error) {
      console.error('Failed to create project:', error);
      alert('Failed to create project');
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        await projectService.deleteProject(projectId);
        loadProjects();
      } catch (error) {
        console.error('Failed to delete project:', error);
        alert('Failed to delete project');
      }
    }
  };

  const handleLogout = () => {
    authService.logout();
    sessionStorage.setItem('skipIntro', 'true'); // Skip intro on next login
    navigate('/home');
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="dashboard-container">
      <Header title="AI PLC Platform" onViewManual={setSelectedManual} />
      
      <div className="dashboard-actions">
        {currentUser?.role === 'admin' && (
          <button onClick={() => navigate('/admin')} className="btn-secondary">
            Manage Employees
          </button>
        )}
        <button onClick={() => setShowCreateModal(true)} className="btn-primary">
          + New Project
        </button>
      </div>

      <div className="dashboard-content">
        <h2>My Projects</h2>
        
        {projects.length === 0 ? (
          <div className="empty-state">
            <p>No projects yet. Create your first project to get started!</p>
            <button onClick={() => setShowCreateModal(true)} className="btn-primary">
              Create Project
            </button>
          </div>
        ) : (
          <div className="projects-grid">
            {projects.map((project) => (
              <div key={project.id} className="project-card">
                <div className="project-card-header">
                  <div>
                    <h3>{project.name}</h3>
                    {project.owner_username && (
                      <span className="project-owner">
                        Created by: {project.owner_username}
                      </span>
                    )}
                  </div>
                  <div className="project-menu">
                    <button 
                      className="btn-menu"
                      onClick={(e) => {
                        e.stopPropagation();
                        setOpenMenuId(openMenuId === project.id ? null : project.id);
                      }}
                    >
                      ⋮
                    </button>
                    {openMenuId === project.id && (
                      <div className="dropdown-menu">
                        {(currentUser?.role === 'admin' || project.owner_id === currentUser?.id) && (
                          <button onClick={() => handleShareClick(project)}>
                            Share with Employee
                          </button>
                        )}
                        <button onClick={() => handleDeleteProject(project.id)}>
                          Delete Project
                        </button>
                      </div>
                    )}
                  </div>
                </div>
                <p>{project.description || 'No description'}</p>
                <div className="project-actions">
                  <button 
                    onClick={() => navigate(`/workspace/${project.id}`)}
                    className="btn-primary"
                  >
                    Open
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Project</h2>
            <form onSubmit={handleCreateProject}>
              <div className="form-group">
                <label>Project Name</label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  required
                  placeholder="e.g., Conveyor Belt System"
                />
              </div>
              <div className="form-group">
                <label>Description (Optional)</label>
                <textarea
                  value={projectDescription}
                  onChange={(e) => setProjectDescription(e.target.value)}
                  placeholder="Describe your PLC project..."
                  rows="4"
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowCreateModal(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showShareModal && selectedProject && (
        <div className="modal-overlay" onClick={() => setShowShareModal(false)}>
          <div className="modal share-modal" onClick={(e) => e.stopPropagation()}>
            <h2>Share "{selectedProject.name}"</h2>
            
            <div className="share-section">
              <h3>Currently Shared With:</h3>
              {sharedEmployees.length === 0 ? (
                <p className="empty-message">Not shared with anyone yet</p>
              ) : (
                <ul className="shared-list">
                  {sharedEmployees.map((share) => (
                    <li key={share.id}>
                      <span>{share.shared_with.username} ({share.shared_with.email})</span>
                      <button 
                        onClick={() => handleUnshareProject(share.shared_with.id)}
                        className="btn-danger-small"
                      >
                        Remove
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="share-section">
              <h3>Share with Employee:</h3>
              {employees.length === 0 ? (
                <p className="empty-message">No employees available</p>
              ) : (
                <ul className="employee-list">
                  {employees
                    .filter(emp => !sharedEmployees.find(s => s.shared_with.id === emp.id))
                    .map((employee) => (
                      <li key={employee.id}>
                        <span>{employee.username} ({employee.email})</span>
                        <button 
                          onClick={() => handleShareProject(employee.id)}
                          className="btn-primary-small"
                        >
                          Share
                        </button>
                      </li>
                    ))}
                </ul>
              )}
            </div>

            <div className="modal-actions">
              <button onClick={() => setShowShareModal(false)} className="btn-secondary">
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {selectedManual && (
        <PDFViewer manual={selectedManual} onClose={() => setSelectedManual(null)} />
      )}
    </div>
  );
}

export default ProjectDashboard;