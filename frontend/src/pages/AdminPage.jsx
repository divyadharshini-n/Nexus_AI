import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import '../styles/Admin.css';

function AdminPage() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [currentUser, setCurrentUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadCurrentUser();
  }, []);

  const loadCurrentUser = async () => {
    try {
      const user = await authService.getCurrentUser();
      setCurrentUser(user);
      
      // Check if user is admin
      if (user.role !== 'admin') {
        alert('Access denied. Admin only.');
        navigate('/dashboard');
        return;
      }
      
      loadEmployees();
    } catch (error) {
      console.error('Failed to load user:', error);
      navigate('/login');
    }
  };

  const loadEmployees = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/admin/employees', {
        headers: {
          'Authorization': `Bearer ${authService.getToken()}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setEmployees(data);
      } else {
        console.error('Failed to load employees');
      }
    } catch (error) {
      console.error('Failed to load employees:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateEmployee = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch('http://localhost:8000/api/admin/employees', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authService.getToken()}`
        },
        body: JSON.stringify({
          username,
          email,
          password,
          full_name: fullName
        })
      });

      if (response.ok) {
        setShowCreateModal(false);
        setUsername('');
        setEmail('');
        setPassword('');
        setFullName('');
        loadEmployees();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to create employee');
      }
    } catch (error) {
      console.error('Failed to create employee:', error);
      alert('Failed to create employee');
    }
  };

  const handleToggleActive = async (employeeId, currentStatus) => {
    try {
      const response = await fetch(`http://localhost:8000/api/admin/employees/${employeeId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authService.getToken()}`
        },
        body: JSON.stringify({
          is_active: !currentStatus
        })
      });

      if (response.ok) {
        loadEmployees();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to update employee');
      }
    } catch (error) {
      console.error('Failed to update employee:', error);
      alert('Failed to update employee');
    }
  };

  const handleDeleteEmployee = async (employeeId) => {
    if (!window.confirm('Are you sure you want to deactivate this employee?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/admin/employees/${employeeId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authService.getToken()}`
        }
      });

      if (response.ok) {
        loadEmployees();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to delete employee');
      }
    } catch (error) {
      console.error('Failed to delete employee:', error);
      alert('Failed to delete employee');
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="admin-container">
      <header className="admin-header">
        <h1>Employee Management</h1>
        <div className="header-actions">
          <button onClick={() => navigate('/dashboard')} className="btn-secondary">
            Back to Dashboard
          </button>
          <button onClick={() => setShowCreateModal(true)} className="btn-primary">
            + Create Employee
          </button>
        </div>
      </header>

      <div className="admin-content">
        <div className="employees-table">
          <table>
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Full Name</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.length === 0 ? (
                <tr>
                  <td colSpan="6" className="empty-cell">
                    No employees yet. Create one to get started.
                  </td>
                </tr>
              ) : (
                employees.map((employee) => (
                  <tr key={employee.id}>
                    <td>{employee.username}</td>
                    <td>{employee.email}</td>
                    <td>{employee.full_name || '-'}</td>
                    <td>
                      <span className={`status-badge ${employee.is_active ? 'active' : 'inactive'}`}>
                        {employee.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>{new Date(employee.created_at).toLocaleDateString()}</td>
                    <td className="actions-cell">
                      <button 
                        onClick={() => handleToggleActive(employee.id, employee.is_active)}
                        className="btn-small btn-secondary"
                      >
                        {employee.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                      <button 
                        onClick={() => handleDeleteEmployee(employee.id)}
                        className="btn-small btn-danger"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Employee</h2>
            <form onSubmit={handleCreateEmployee}>
              <div className="form-group">
                <label>Username *</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  placeholder="employee_username"
                />
              </div>
              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="employee@example.com"
                />
              </div>
              <div className="form-group">
                <label>Password *</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  minLength="6"
                />
              </div>
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="John Doe"
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowCreateModal(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Create Employee
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminPage;
