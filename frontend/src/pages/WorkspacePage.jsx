import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import projectService from '../services/projectService';
import nexusAIService from '../services/nexusAIService';
import aiDudeService from '../services/aiDudeService';
import plannerService from '../services/plannerService';
import codeGenerationService from '../services/codeGenerationService';
import exportService from '../services/exportService';
import stageService from '../services/stageService';
import raSystemService from '../services/raSystemService';
import authService from '../services/authService';
import Header from '../components/common/Header';
import PDFViewer from '../components/common/PDFViewer';
import FileUpload from '../components/workspace/input/FileUpload';
import StageEditor from '../components/workspace/stage/StageEditor';
import CodeEditor from '../components/workspace/code/CodeEditor';
import ValidationResults from '../components/workspace/stage/ValidationResults';
import VersionHistoryModal from '../components/workspace/stage/VersionHistoryModal';
import SafetyManualUpload from '../components/workspace/ra/SafetyManualUpload';
import SafetyAssessmentResults from '../components/workspace/ra/SafetyAssessmentResults';
import CodeBlockTabs from '../components/workspace/code/CodeBlockTabs';
import '../styles/Workspace.css';
import SafetyCheckResults from '../components/workspace/ra/SafetyCheckResults';
import reportsService from '../services/reportsService';

function WorkspacePage() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const aiDudeTextareaRef = useRef(null);
  const [project, setProject] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [showAiDude, setShowAiDude] = useState(false);
  const [aiDudeMessages, setAiDudeMessages] = useState([]);
  const [aiDudeInput, setAiDudeInput] = useState('');
  const [aiDudeLoading, setAiDudeLoading] = useState(false);
  const [safetyCheckResult, setSafetyCheckResult] = useState(null);
  const [performingSafetyCheck, setPerformingSafetyCheck] = useState(false);
  const [defaultSafetyReady, setDefaultSafetyReady] = useState(false);
  const [generatingCode, setGeneratingCode] = useState(false);
  const [codeGenCompleted, setCodeGenCompleted] = useState(false);
  const [planCompleted, setPlanCompleted] = useState(false);
  const [validateCompleted, setValidateCompleted] = useState(false);
  const [safetyCheckCompleted, setSafetyCheckCompleted] = useState(false);

  // Planner states
  const [showPlanner, setShowPlanner] = useState(false);
  const [inputMode, setInputMode] = useState('text'); // 'text' or 'file'
  const [controlLogic, setControlLogic] = useState('');
  const [plannerLoading, setPlannerLoading] = useState(false);
  const [stages, setStages] = useState([]);
  const [selectedStage, setSelectedStage] = useState(null);

  // Stage management states
  const [editingStage, setEditingStage] = useState(false);
  const [showExportDropdown, setShowExportDropdown] = useState(false);
  const [editingCode, setEditingCode] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [validating, setValidating] = useState(false);
  const [activeView, setActiveView] = useState(null); // 'validation', 'code', 'safety'
  const [showVersionHistory, setShowVersionHistory] = useState(false);

  // RA System states
  const [showSafetyPanel, setShowSafetyPanel] = useState(false);
  const [safetyManualExists, setSafetyManualExists] = useState(false);
  const [safetyAssessment, setSafetyAssessment] = useState(null);
  const [interrogating, setInterrogating] = useState(false);
  const [selectedManual, setSelectedManual] = useState(null);

  useEffect(() => {
    loadProject();
    loadStages();
    checkDefaultSafetyStatus();
  }, [projectId]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showExportDropdown && !event.target.closest('.export-dropdown-container')) {
        setShowExportDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showExportDropdown]);

  const loadProject = async () => {
    try {
      const data = await projectService.getProject(projectId);
      setProject(data);
      await checkSafetyManual();
    } catch (error) {
      console.error('Failed to load project:', error);
      navigate('/dashboard');
    }
  };
  const checkDefaultSafetyStatus = async () => {
  try {
    const status = await raSystemService.getDefaultSafetyStatus();
    setDefaultSafetyReady(status.ready);
  } catch (error) {
    console.error('Failed to check default safety status:', error);
  }
};
  const loadStages = async () => {
    try {
      const data = await plannerService.getProjectStages(projectId);
      setStages(data.stages || []);
    } catch (error) {
      console.error('Failed to load stages:', error);
    }
  };

  const checkSafetyManual = async () => {
    try {
      const status = await raSystemService.getSafetyManualStatus(projectId);
      setSafetyManualExists(status.exists);
    } catch (error) {
      console.error('Failed to check safety manual:', error);
    }
  };

  const handleTextExtracted = (extractedText) => {
    setControlLogic(extractedText);
    setInputMode('text');
    alert('Text extracted successfully! You can now edit or create the plan.');
  };

  const handleCreatePlan = async (e) => {
    e.preventDefault();
    if (!controlLogic.trim()) return;

    setPlannerLoading(true);
    setPlanCompleted(false);
    try {
      const result = await plannerService.createPlan(projectId, controlLogic);
      
      if (result.success) {
        setPlanCompleted(true);
        setTimeout(() => {
          alert(`Plan created successfully! ${result.total_stages} stages generated.`);
          setStages(result.stages || []);
          setShowPlanner(false);
          setControlLogic('');
          loadStages();
          setTimeout(() => setPlanCompleted(false), 500);
        }, 300);
      } else {
        alert(`Failed to create plan: ${result.error}`);
      }
    } catch (error) {
      console.error('Failed to create plan:', error);
      alert('Failed to create plan');
    } finally {
      setPlannerLoading(false);
    }
  };

  const handleGenerateCode = async (stage) => {
    // Check if all stages are validated
    const allStagesValidated = stages.every(s => s.is_validated === true);
    
    if (!allStagesValidated) {
      alert('All stages must be validated before generating code. Please validate all stages first.');
      return;
    }
    
    setGeneratingCode(true);
    setCodeGenCompleted(false);
    try {
      const result = await codeGenerationService.generateCode(stage.id);
      if (result.success) {
        setCodeGenCompleted(true);
        
        // Reload all stages to get updated generated code for all of them
        await loadStages();
        
        // Fetch generated code for the current stage to display
        try {
          const codeResult = await codeGenerationService.getGeneratedCode(stage.id);
          if (codeResult.success) {
            setSelectedStage({...stage, generatedCode: codeResult});
          }
        } catch (err) {
          console.error('Failed to fetch generated code:', err);
        }
        
        setTimeout(() => {
          alert('Code generated successfully for ALL stages!');
          setActiveView('code'); // Show code view when generated
          setTimeout(() => setCodeGenCompleted(false), 500);
        }, 300);
      } else {
        alert('Failed to generate code');
      }
    } catch (error) {
      console.error('Code generation error:', error);
      alert('Failed to generate code');
    } finally {
      setGeneratingCode(false);
    }
  };
  const handlePerformSafetyCheck = async () => {
  if (!defaultSafetyReady) {
    alert('Default safety manuals not loaded. Please contact administrator.');
    return;
  }

  setPerformingSafetyCheck(true);
  setSafetyCheckCompleted(false);
  setSafetyCheckResult(null);
  try {
    const result = await raSystemService.performSafetyCheck(selectedStage.id);
    setSafetyCheckResult(result);
    setActiveView('safety'); // Show safety check view
    
    setSafetyCheckCompleted(true);
    setTimeout(() => {
      if (result.passed) {
        alert(`Safety Check: ${result.status} - Code meets safety requirements`);
      } else {
        alert(`Safety Check: ${result.status} - Safety issues found. Please review.`);
      }
      setTimeout(() => setSafetyCheckCompleted(false), 500);
    }, 300);
  } catch (error) {
    console.error('Safety check error:', error);
    alert('Failed to perform safety check. Make sure code is generated.');
  } finally {
    setPerformingSafetyCheck(false);
  }
};

  const handleExportStage = async (stageId) => {
    const result = await exportService.exportStageCSV(stageId);
    if (result.success) {
      alert('Stage code exported successfully!');
    } else {
      alert('Export failed: ' + result.error);
    }
  };

  const handleExportLabels = async () => {
    if (!selectedStage || !selectedStage.generatedCode) {
      alert('No code generated for this stage. Please generate code first.');
      return;
    }
    
    try {
      const token = authService.getToken();
      if (!token) {
        alert('Please login to export labels');
        navigate('/login');
        return;
      }
      
      const response = await fetch(`http://localhost:8000/api/code/stage/${selectedStage.id}/export-labels`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'text/csv'
        }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Labels_Stage_${selectedStage.stage_number}_${selectedStage.stage_name.replace(/\s+/g, '_')}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        const error = await response.json().catch(() => ({ detail: 'Failed to export labels' }));
        alert(error.detail || 'Failed to export labels');
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export labels. Please try again.');
    }
  };

  const handleExportAllLabels = async () => {
    if (!project) {
      alert('Project not loaded');
      return;
    }
    
    try {
      const token = authService.getToken();
      if (!token) {
        alert('Please login to export labels');
        navigate('/login');
        return;
      }
      
      const response = await fetch(`http://localhost:8000/api/code/project/${project.id}/export-all-labels`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'text/csv'
        }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `All_Labels_${project.name.replace(/\s+/g, '_')}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        alert('All labels exported successfully!');
      } else {
        const error = await response.json().catch(() => ({ detail: 'Failed to export labels' }));
        alert(error.detail || 'Failed to export labels');
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export all labels. Please try again.');
    }
    setShowExportDropdown(false);
  };

  const handleExportStageLocalLabels = async (stageId, stageName) => {
    if (!project) {
      alert('Project not loaded');
      return;
    }
    
    try {
      const token = authService.getToken();
      if (!token) {
        alert('Please login to export labels');
        navigate('/login');
        return;
      }
      
      console.log('Exporting labels for stage:', stageId, stageName);
      const response = await fetch(`http://localhost:8000/api/code/stage/${stageId}/export-labels`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'text/csv'
        }
      });
      
      console.log('Response status:', response.status);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${stageName.replace(/\s+/g, '_')}_Local_Labels.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        alert(`${stageName} local labels exported successfully!`);
      } else {
        const errorText = await response.text();
        console.error('Export error response:', errorText);
        try {
          const error = JSON.parse(errorText);
          alert(`Export failed: ${error.detail || 'Unknown error'}`);
        } catch (e) {
          alert(`Export failed: ${errorText || 'Failed to export labels'}`);
        }
      }
    } catch (error) {
      console.error('Export error:', error);
      alert(`Failed to export stage labels: ${error.message}`);
    }
    setShowExportDropdown(false);
  };

  const handleExportGlobalLabels = async () => {
    if (!project) {
      alert('Project not loaded');
      return;
    }
    
    try {
      const token = authService.getToken();
      if (!token) {
        alert('Please login to export labels');
        navigate('/login');
        return;
      }
      
      const response = await fetch(`http://localhost:8000/api/code/project/${project.id}/export-global-labels`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'text/csv'
        }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${project.name.replace(/\s+/g, '_')}_Global_Labels.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        alert('Global labels exported successfully!');
      } else {
        const error = await response.json().catch(() => ({ detail: 'Failed to export global labels' }));
        alert(error.detail || 'Failed to export global labels');
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export global labels. Please try again.');
    }
    setShowExportDropdown(false);
  };

  const handleEditStage = () => {
    setEditingStage(true);
    setActiveView('edit');
  };

  const handleSaveStageEdit = async (editedLogic) => {
    try {
      await stageService.updateStageLogic(selectedStage.id, editedLogic);
      alert('Stage logic updated successfully!');
      setEditingStage(false);
      setActiveView(null);
      await loadStages();
      const updatedStage = {...selectedStage, edited_logic: editedLogic, generatedCode: selectedStage.generatedCode};
      setSelectedStage(updatedStage);
    } catch (error) {
      console.error('Failed to update stage:', error);
      alert('Failed to update stage logic');
    }
  };

  const handleValidateStage = async () => {
    setValidating(true);
    setValidateCompleted(false);
    setValidationResult(null);
    try {
      const result = await stageService.validateStage(selectedStage.id);
      setValidationResult(result);
      setActiveView('validation'); // Show validation view
      
      setValidateCompleted(true);
      setTimeout(() => {
        if (result.valid) {
          alert('Stage validation passed!');
          loadStages();
          const updatedStage = {...selectedStage, is_validated: true, generatedCode: selectedStage.generatedCode};
          setSelectedStage(updatedStage);
        } else {
          // Show descriptive failure message
          let failureReason = 'Validation failed';
          if (result.issues && result.issues.length > 0) {
            const firstIssue = result.issues[0];
            if (firstIssue.length > 80) {
              failureReason = `Validation failed: ${firstIssue.substring(0, 77)}...`;
            } else {
              failureReason = `Validation failed: ${firstIssue}`;
            }
          }
          alert(failureReason);
        }
        setTimeout(() => setValidateCompleted(false), 500);
      }, 300);
    } catch (error) {
      console.error('Validation error:', error);
      alert('Failed to validate stage');
    } finally {
      setValidating(false);
    }
  };

  const handleFinalizeStage = async () => {
    if (!selectedStage.is_validated) {
      alert('Stage must be validated before finalizing');
      return;
    }
    
    if (!window.confirm('Are you sure you want to finalize this stage? It cannot be edited after finalization.')) {
      return;
    }
    
    try {
      await stageService.finalizeStage(selectedStage.id);
      alert('Stage finalized successfully!');
      await loadStages();
      const updatedStage = {...selectedStage, is_finalized: true, generatedCode: selectedStage.generatedCode};
      setSelectedStage(updatedStage);
    } catch (error) {
      console.error('Failed to finalize stage:', error);
      alert('Failed to finalize stage');
    }
  };

  const handleEditCode = () => {
    setEditingCode(true);
    setActiveView('editCode');
  };

  const handleSaveCodeEdit = async (editedCode, globalLabels, localLabels) => {
    try {
      await codeGenerationService.updateCode(selectedStage.id, editedCode, globalLabels, localLabels);
      
      // Reload stage with updated code from backend
      const codeResult = await codeGenerationService.getStageCode(selectedStage.id);
      if (codeResult.success && codeResult.code) {
        // Update selected stage with fresh data from backend
        setSelectedStage({
          ...selectedStage, 
          generatedCode: {
            ...codeResult.code,
            global_labels: codeResult.code.global_labels || [],
            local_labels: codeResult.code.local_labels || []
          }
        });
      }
      
      setEditingCode(false);
      setActiveView('code');
      alert('Code and labels updated successfully!');
    } catch (error) {
      console.error('Failed to update code:', error);
      alert('Failed to update code: ' + (error.message || 'Unknown error'));
    }
  };

  const handleCopyCode = () => {
    if (!selectedStage.generatedCode) return;
    
    const codeText = selectedStage.generatedCode.program_body;
    navigator.clipboard.writeText(codeText).then(() => {
      alert('Code copied to clipboard!');
    }).catch(err => {
      console.error('Failed to copy code:', err);
      alert('Failed to copy code');
    });
  };

  const handleUploadSafetyManual = async (file) => {
    try {
      const result = await raSystemService.uploadSafetyManual(projectId, file);
      alert(`Safety manual uploaded successfully! ${result.chunks_count} chunks processed.`);
      setSafetyManualExists(true);
    } catch (error) {
      console.error('Failed to upload safety manual:', error);
      alert('Failed to upload safety manual');
      throw error;
    }
  };

  const handleInterrogateCode = async () => {
    if (!safetyManualExists) {
      alert('Please upload a safety manual first');
      return;
    }

    setInterrogating(true);
    setSafetyAssessment(null);
    try {
      const result = await raSystemService.interrogateCode(selectedStage.id);
      setSafetyAssessment(result);
      
      if (result.safe) {
        alert(`Safety assessment: ${result.status} - Code meets safety requirements`);
      } else {
        alert(`Safety assessment: ${result.status} - Safety issues found. Please review.`);
      }
    } catch (error) {
      console.error('Interrogation error:', error);
      alert('Failed to interrogate code');
    } finally {
      setInterrogating(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMessage = inputMessage;
    setInputMessage('');
    
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage
    }]);

    setLoading(true);
    try {
      const response = await nexusAIService.chat(projectId, userMessage);
      setMessages(prev => [...prev, {
        role: 'nexus',
        content: response.response,
        phase: response.phase
      }]);
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to get response from Nexus AI');
    } finally {
      setLoading(false);
    }
  };

  const handleAiDudeQuery = async (e) => {
    e.preventDefault();
    if (!aiDudeInput.trim()) return;

    const question = aiDudeInput;
    setAiDudeInput('');
    
    // Reset textarea height
    if (aiDudeTextareaRef.current) {
      aiDudeTextareaRef.current.style.height = '38px';
    }
    
    setAiDudeMessages(prev => [...prev, {
      role: 'user',
      content: question
    }]);

    setAiDudeLoading(true);
    try {
      const response = await aiDudeService.query(projectId, question);
      setAiDudeMessages(prev => [...prev, {
        role: 'aidude',
        content: response.answer
      }]);
    } catch (error) {
      console.error('Failed to query AI Dude:', error);
      alert('Failed to get response from AI Dude');
    } finally {
      setAiDudeLoading(false);
    }
  };

  const handleGenerateDOCXReport = async () => {
    try {
      const result = await reportsService.generateDOCXReport(projectId);
      if (result.success) {
        alert('Technical documentation report generated successfully!');
      } else {
        alert('Failed to generate report: ' + result.error);
      }
    } catch (error) {
      console.error('Report generation error:', error);
      // Check if error response has a detail message
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to generate report';
      alert(errorMessage);
    }
  };

  const handleGenerateAuditTrailReport = async () => {
    try {
      console.log('Generating audit trail report for project:', projectId);
      const result = await reportsService.generateAuditTrailReport(projectId);
      console.log('Audit trail report result:', result);
      if (result.success) {
        alert('Version History & Audit Trail report generated successfully!');
      } else {
        alert('Failed to generate audit trail report: ' + result.error);
      }
    } catch (error) {
      console.error('Audit trail report generation error:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to generate audit trail report';
      alert('Error: ' + errorMessage);
    }
  };

  if (!project) {
    return <div className="loading">Loading project...</div>;
  }

  return (
    <div className="workspace-container">
      <Header title={project.name} onViewManual={setSelectedManual} />
      
      <div className="workspace-actions">
        <button onClick={() => navigate('/dashboard')} className="back-button">
          ← Back to Dashboard
        </button>
        <div className="action-buttons-group">
          {stages.length > 0 && (
            <div className="export-dropdown-container">
              <button 
                onClick={() => setShowExportDropdown(!showExportDropdown)}
                className="btn-export-all-labels"
                title="Export labels from all stages"
              >
                Export All Labels ▾
              </button>
              {showExportDropdown && (
                <div className="export-dropdown-menu">
                  {stages.map((stage, index) => (
                    <button
                      key={stage.id}
                      onClick={() => handleExportStageLocalLabels(stage.id, stage.stage_name)}
                      className="export-dropdown-item"
                    >
                      Stage {index} Local Labels
                    </button>
                  ))}
                  <button
                    onClick={handleExportGlobalLabels}
                    className="export-dropdown-item export-dropdown-global"
                  >
                    Global Labels
                  </button>
                </div>
              )}
            </div>
          )}
          <button 
            onClick={() => setShowSafetyPanel(!showSafetyPanel)}
            className="btn-safety"
          >
            {showSafetyPanel ? 'Hide Safety' : 'Safety System'}
          </button>
          <button 
            onClick={handleGenerateDOCXReport}
            className="btn-report-docx"
            disabled={stages.length === 0}
            title={stages.length === 0 ? "Create stages first to enable report" : "Generate technical documentation report"}
          >
            Word Report
          </button>
          <button
            onClick={handleGenerateAuditTrailReport}
            className="btn-version-history"
            title="Generate Version History & Audit Trail Report"
          >
            Version History
          </button>
          <button onClick={() => setShowPlanner(!showPlanner)} className="btn-planner">
            {showPlanner ? 'Hide Planner' : 'Create Plan'}
          </button>
          <button 
            onClick={() => setShowAiDude(!showAiDude)} 
            className="btn-aidude"
            title={showAiDude ? 'Hide AI Dude' : 'Ask AI Dude'}
            aria-label={showAiDude ? 'Hide AI Dude' : 'Ask AI Dude'}
          >
          </button>
        </div>
      </div>

      <div className="workspace-content">
        {/* Stages Sidebar */}
        {stages.length > 0 && (
          <div className="stages-sidebar">
            <h3>Stages ({stages.length})</h3>
            <div className="stages-list">
              {stages.map((stage) => (
                <div
                  key={stage.id}
                  className={`stage-item ${selectedStage?.id === stage.id ? 'active' : ''}`}
                  onClick={async () => {
                    // Load generated code for this stage if it exists
                    try {
                      const codeResult = await codeGenerationService.getStageCode(stage.id);
                      if (codeResult.success && codeResult.code) {
                        setSelectedStage({...stage, generatedCode: codeResult.code});
                      } else {
                        setSelectedStage(stage);
                      }
                    } catch (error) {
                      console.error('Error loading stage code:', error);
                      setSelectedStage(stage);
                    }
                    setEditingStage(false);
                    setActiveView(null);
                    setSafetyAssessment(null);
                  }}
                >
                  <div className="stage-number">Stage {stage.stage_number}</div>
                  <div className="stage-name">{stage.stage_name}</div>
                  <div className="stage-type">{stage.stage_type}</div>
                  {stage.is_finalized && <div className="stage-finalized">Finalized</div>}
                  {stage.is_validated && !stage.is_finalized && <div className="stage-validated">Validated</div>}
                </div>
              ))}
            </div>
            
            {/* Export Labels Buttons */}
            <div className="stages-actions">
              {/* Export Current Stage Labels */}
              {selectedStage && selectedStage.generatedCode && (
                <button 
                  onClick={handleExportLabels}
                  className="btn-export-labels"
                  title="Export labels from selected stage"
                >
                  <span className="icon"></span>
                  <span className="text">Export Stage Labels</span>
                </button>
              )}
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="main-content">
          {/* Welcome Panel - Show when stages exist but none selected and planner is closed */}
          {stages.length > 0 && !selectedStage && !showPlanner && (
            <div className="welcome-panel">
              <div className="welcome-content">
                <div className="welcome-icon"></div>
                <h2>Plan Created Successfully!</h2>
                <p className="welcome-message">
                  Your control logic has been analyzed and broken down into {stages.length} stages.
                </p>
                
                {/* Removed white box with instructions as requested */}

                <div className="welcome-stats">
                  <div className="stat-card">
                    <div className="stat-value">{stages.length}</div>
                    <div className="stat-label">Total Stages</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{stages.filter(s => s.is_validated).length}</div>
                    <div className="stat-label">Validated</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{stages.filter(s => s.is_finalized).length}</div>
                    <div className="stat-label">Finalized</div>
                  </div>
                </div>

                <div className="welcome-actions">
                  <button 
                    className="btn-primary-large"
                    onClick={async () => {
                      const stage = stages[0];
                      try {
                        const codeResult = await codeGenerationService.getStageCode(stage.id);
                        if (codeResult.success && codeResult.code) {
                          setSelectedStage({...stage, generatedCode: codeResult.code});
                        } else {
                          setSelectedStage(stage);
                        }
                      } catch (error) {
                        console.error('Error loading stage code:', error);
                        setSelectedStage(stage);
                      }
                    }}
                  >
                    Start with Stage 1
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Planner Panel */}
          {showPlanner && (
            <div className="planner-panel">
              <h2>Create Execution Plan</h2>
              
              {/* Input Mode Selector */}
              <div className="input-mode-selector">
                <button
                  className={`mode-btn ${inputMode === 'text' ? 'active' : ''}`}
                  onClick={() => setInputMode('text')}
                >
                  Text Input
                </button>
                <button
                  className={`mode-btn ${inputMode === 'file' ? 'active' : ''}`}
                  onClick={() => setInputMode('file')}
                >
                  Upload File
                </button>
              </div>

              {/* Text Input Mode */}
              {inputMode === 'text' && (
                <>
                  <p className="planner-info">
                    Describe your complete control logic (minimum 50 words). 
                    The system will analyze and segregate it into stages.
                  </p>
                  <form onSubmit={handleCreatePlan} className="planner-input-form">
                    <textarea
                      value={controlLogic}
                      onChange={(e) => setControlLogic(e.target.value)}
                      placeholder="Describe your complete PLC control system...&#10;&#10;Example: This is a conveyor belt system with start/stop buttons, emergency stop, product detection sensors, and safety interlocks..."
                      rows="12"
                      disabled={plannerLoading}
                    />
                    <button 
                      type="submit" 
                      disabled={plannerLoading || controlLogic.split(/\s+/).filter(w => w).length < 50}
                    >
                      {plannerLoading ? 'Creating Plan...' : 'Create Plan'}
                      {(plannerLoading || planCompleted) && (
                        <span className="circular-progress">
                          <svg className="progress-ring" width="20" height="20" key={plannerLoading ? 'loading' : 'completed'}>
                            <circle
                              className={`progress-ring-circle ${planCompleted ? 'completed' : ''}`}
                              stroke="white"
                              strokeWidth="2"
                              fill="transparent"
                              r="8"
                              cx="10"
                              cy="10"
                            />
                          </svg>
                        </span>
                      )}
                    </button>
                  </form>
                  {controlLogic.split(/\s+/).filter(w => w).length < 50 && (
                    <p className="word-count-hint">
                      {controlLogic.split(/\s+/).filter(w => w).length} words (minimum 50 required)
                    </p>
                  )}
                </>
              )}

              {/* File Upload Mode */}
              {inputMode === 'file' && (
                <>
                  <p className="planner-info">
                    Upload a file containing your control logic (TXT, PDF, DOCX, or WAV audio).
                    The text will be extracted automatically.
                  </p>
                  <FileUpload projectId={projectId} onTextExtracted={handleTextExtracted} />
                </>
              )}
            </div>
          )}

          {/* Stage Detail View */}
          {selectedStage && !showPlanner && (
            <div className="stage-detail">
              <div className="stage-header">
                <h2>Stage {selectedStage.stage_number}: {selectedStage.stage_name}</h2>
                <div className="stage-actions">
                  <span className={`stage-badge ${selectedStage.stage_type}`}>
                    {selectedStage.stage_type}
                  </span>
                  
                  {!selectedStage.is_finalized && (
                    <>
                      <button 
                        onClick={handleEditStage}
                        className="btn-edit-stage"
                      >
                        Edit Logic
                      </button>
                      <button 
                        onClick={handleValidateStage}
                        disabled={validating}
                        className="btn-validate-stage"
                      >
                        {validating ? 'Validating...' : 'Validate'}
                        {(validating || validateCompleted) && (
                          <span className="circular-progress">
                            <svg className="progress-ring" width="20" height="20" key={validating ? 'validating' : 'completed'}>
                              <circle
                                className={`progress-ring-circle ${validateCompleted ? 'completed' : ''}`}
                                stroke="white"
                                strokeWidth="2"
                                fill="transparent"
                                r="8"
                                cx="10"
                                cy="10"
                              />
                            </svg>
                          </span>
                        )}
                      </button>
                    </>
                  )}
                  
                  <button 
                    onClick={() => handleGenerateCode(selectedStage)}
                    className="btn-generate-code"
                    disabled={!stages.every(s => s.is_validated === true) || generatingCode}
                    title={!stages.every(s => s.is_validated === true) ? 
                      'All stages must be validated before generating code' : 
                      'Generate code for this stage'}
                  >
                    Generate Code
                    {(generatingCode || codeGenCompleted) && (
                      <span className="circular-progress">
                        <svg className="progress-ring" width="20" height="20" key={generatingCode ? 'generating' : 'completed'}>
                          <circle
                            className={`progress-ring-circle ${codeGenCompleted ? 'completed' : ''}`}
                            stroke="white"
                            strokeWidth="2"
                            fill="transparent"
                            r="8"
                            cx="10"
                            cy="10"
                          />
                        </svg>
                      </span>
                    )}
                  </button>
                  <button 
  onClick={handlePerformSafetyCheck}
  disabled={performingSafetyCheck || !defaultSafetyReady}
  className="btn-safety-check"
  title={!defaultSafetyReady ? 'Default safety manuals not loaded' : 'Check code against safety standards'}
>
  {performingSafetyCheck ? 'Checking...' : 'Safety Check'}
  {(performingSafetyCheck || safetyCheckCompleted) && (
    <span className="circular-progress">
      <svg className="progress-ring" width="20" height="20" key={performingSafetyCheck ? 'checking' : 'completed'}>
        <circle
          className={`progress-ring-circle ${safetyCheckCompleted ? 'completed' : ''}`}
          stroke="white"
          strokeWidth="2"
          fill="transparent"
          r="8"
          cx="10"
          cy="10"
        />
      </svg>
    </span>
  )}
</button>
                </div>
              </div>
              
              {/* View Toggle Buttons */}
              {(editingStage || validationResult || selectedStage.generatedCode || safetyCheckResult) && (
                <div className="view-toggle-buttons">
                  {editingStage && (
                    <button
                      className={`view-toggle-btn ${activeView === 'edit' ? 'active' : ''}`}
                      onClick={() => setActiveView('edit')}
                    >
                      Edit Logic
                    </button>
                  )}
                  {validationResult && (
                    <button
                      className={`view-toggle-btn ${activeView === 'validation' ? 'active' : ''}`}
                      onClick={() => setActiveView('validation')}
                    >
                      Validation Results
                    </button>
                  )}
                  {selectedStage.generatedCode && (
                    <button
                      className={`view-toggle-btn ${activeView === 'code' ? 'active' : ''}`}
                      onClick={() => setActiveView('code')}
                    >
                      Generated Code
                    </button>
                  )}
                  {safetyCheckResult && (
                    <button
                      className={`view-toggle-btn ${activeView === 'safety' ? 'active' : ''}`}
                      onClick={() => setActiveView('safety')}
                    >
                      Safety Check
                    </button>
                  )}
                </div>
              )}

              {/* Stage Editor */}
              {editingStage && activeView === 'edit' && (
                <StageEditor
                  stage={selectedStage}
                  onSave={handleSaveStageEdit}
                  onCancel={() => {
                    setEditingStage(false);
                    setActiveView(null);
                  }}
                />
              )}

              {/* Code Editor */}
              {editingCode && activeView === 'editCode' && selectedStage.generatedCode && (
                <CodeEditor
                  code={selectedStage.generatedCode}
                  onSave={handleSaveCodeEdit}
                  onCancel={() => {
                    setEditingCode(false);
                    setActiveView('code');
                  }}
                />
              )}

              {/* Validation Results */}
              {validationResult && activeView === 'validation' && (
                <ValidationResults validation={validationResult} />
              )}
              
              <div className="stage-description">
                <h3>Description</h3>
                <p>{selectedStage.description}</p>
              </div>
              
              <div className="stage-logic">
                <h3>Original Logic</h3>
                <pre>{selectedStage.original_logic}</pre>
              </div>
              
              {selectedStage.edited_logic && (
                <div className="stage-logic">
                  <h3>Edited Logic</h3>
                  <pre>{selectedStage.edited_logic}</pre>
                </div>
              )}
              
              {/* Generated Code Section */}
              {selectedStage.generatedCode && activeView === 'code' && (
                <div className="generated-code-section">
                  <div className="code-header-with-actions">
                    <h3>Generated Structured Text Code</h3>
                    <div className="code-actions">
                      <button 
                        onClick={handleEditCode}
                        className="btn-edit-code"
                        title="Edit Code"
                      >
                        Edit Code
                      </button>
                      <button 
                        onClick={handleCopyCode}
                        className="btn-copy-code"
                        title="Copy Code"
                      >
                        Copy Code
                      </button>
                    </div>
                  </div>
                  
                  {/* Use new CodeBlockTabs component */}
                  <CodeBlockTabs generatedCode={selectedStage.generatedCode} />
                </div>
              )}
              
              <div className="stage-status">
                <span>Validated: {selectedStage.is_validated ? '☑️' : '❌'}</span>
                <span>Finalized: {selectedStage.is_finalized ? '☑️' : '❌'}</span>
                {selectedStage.version_number && (
                  <span className="version-badge">Version: {selectedStage.version_number}</span>
                )}
                {selectedStage.last_action && (
                  <span className="last-action">Last Action: {selectedStage.last_action}</span>
                )}
              </div>
            </div>
          )}
          {/* Safety Check Results */}
{safetyCheckResult && activeView === 'safety' && (
  <SafetyCheckResults checkResult={safetyCheckResult} />
)}

          {/* Nexus Chat (when no stage selected and planner hidden) */}
          {!selectedStage && !showPlanner && (
            <div className="nexus-chat">
              <div className="chat-messages">
                {messages.length === 0 && (
                  <div className="welcome-message">
                    <h2>Welcome to Nexus AI</h2>
                    <p>Start by creating a plan.</p>
                  </div>
                )}
                
                {messages.map((msg, index) => (
                  <div key={index} className={`message ${msg.role}`}>
                    <div className="message-header">
                      {msg.role === 'user' ? 'You' : 'Nexus AI'}
                      {msg.phase && <span className="phase-badge">{msg.phase}</span>}
                    </div>
                    <div className="message-content">
                      {msg.content}
                    </div>
                  </div>
                ))}
                
                {loading && (
                  <div className="message nexus">
                    <div className="message-header">Nexus AI</div>
                    <div className="message-content typing">Thinking...</div>
                  </div>
                )}
              </div>

              {messages.length === 0 ? (
                <div className="chat-input-form">
                  <button 
                    onClick={() => setShowPlanner(true)}
                    className="btn-create-plan-large"
                  >
                    Create Plan
                  </button>
                </div>
              ) : (
                <form onSubmit={handleSendMessage} className="chat-input-form">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Chat with Nexus AI..."
                    rows="3"
                    disabled={loading}
                  />
                  <button type="submit" disabled={loading || !inputMessage.trim()}>
                    Send
                  </button>
                </form>
              )}
            </div>
          )}
        </div>

        {/* Safety Panel */}
        {showSafetyPanel && (
          <div className="safety-panel">
            <h3> Safety Assessment System</h3>
            
            <div className="safety-panel-content">
              {!safetyManualExists ? (
                <SafetyManualUpload 
                  projectId={projectId} 
                  onUploadSuccess={handleUploadSafetyManual}
                />
              ) : (
                <div className="safety-manual-status">
                  <div className="status-check">
                    Safety manual uploaded
                  </div>
                  <button 
                    onClick={() => {
                      if (window.confirm('Upload a new safety manual? This will replace the existing one.')) {
                        setSafetyManualExists(false);
                        setSafetyAssessment(null);
                      }
                    }}
                    className="btn-replace-manual"
                  >
                    Replace Manual
                  </button>
                </div>
              )}

              {selectedStage && selectedStage.generatedCode && (
                <div className="interrogation-section">
                  <h4>Interrogate Generated Code</h4>
                  <p className="interrogation-info">
                    Validate the generated code against your safety manual to identify potential hazards.
                  </p>
                  <button
                    onClick={handleInterrogateCode}
                    disabled={interrogating || !safetyManualExists}
                    className="btn-interrogate"
                  >
                    {interrogating ? 'Interrogating...' : '🔍 Run Safety Check'}
                  </button>
                </div>
              )}

              {safetyAssessment && (
                <SafetyAssessmentResults assessment={safetyAssessment} />
              )}
            </div>
          </div>
        )}

        {/* AI Dude Panel */}
        {showAiDude && (
          <div className="aidude-panel">
            <h3>AI Dude - Expert Assistant</h3>
            
            <div className="aidude-messages">
              {aiDudeMessages.length === 0 && (
                <div className="aidude-welcome">
                  <p>Ask me anything about GX Works3, FX5U, or the generated code!</p>
                </div>
              )}
              
              {aiDudeMessages.map((msg, index) => (
                <div key={index} className={`aidude-message ${msg.role}`}>
                  <div className="message-header">
                    {msg.role === 'user' ? 'You' : 'AI Dude'}
                  </div>
                  <div className="message-content">
                    {msg.content}
                  </div>
                </div>
              ))}
              
              {aiDudeLoading && (
                <div className="aidude-message aidude">
                  <div className="message-header">AI Dude</div>
                  <div className="message-content typing">Generating...</div>
                </div>
              )}
            </div>

            <form onSubmit={handleAiDudeQuery} className="aidude-input-form">
              <textarea
                ref={aiDudeTextareaRef}
                value={aiDudeInput}
                onChange={e => {
                  setAiDudeInput(e.target.value);
                  // Auto-resize
                  const ta = e.target;
                  ta.style.height = 'auto';
                  ta.style.height = ta.scrollHeight + 'px';
                }}
                placeholder="Ask a question..."
                disabled={aiDudeLoading}
                rows={1}
                style={{resize: 'none', minHeight: '38px', maxHeight: '200px', overflow: 'auto'}}
                className="aidude-textarea"
              />
              <button type="submit" disabled={aiDudeLoading || !aiDudeInput.trim()}>
                Ask
              </button>
            </form>
          </div>
        )}
      </div>
      
      {/* Version History Modal */}
      {showVersionHistory && (
        selectedStage ? (
          <VersionHistoryModal
            stage={selectedStage}
            onClose={() => setShowVersionHistory(false)}
          />
        ) : (
          <div className="modal-overlay" onClick={() => setShowVersionHistory(false)}>
            <div className="modal-content-small" onClick={(e) => e.stopPropagation()}>
              <h2>Version History</h2>
              <p>
                Please select a stage from the left sidebar to view its version history.
              </p>
              <button 
                onClick={() => setShowVersionHistory(false)}
                className="btn-primary"
              >
                Close
              </button>
            </div>
          </div>
        )
      )}

      {selectedManual && (
        <PDFViewer manual={selectedManual} onClose={() => setSelectedManual(null)} />
      )}
    </div>
  );
}

export default WorkspacePage;