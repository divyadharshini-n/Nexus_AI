import React, { useState } from 'react';
import '../../../styles/CodeBlockTabs.css';

function CodeBlockTabs({ generatedCode }) {
  const [activeTab, setActiveTab] = useState('program');

  // Check if we have the new structure
  const hasNewStructure = generatedCode.program_blocks || generatedCode.functions || generatedCode.function_blocks;

  return (
    <div className="code-block-tabs-container">
      {/* Tab Navigation */}
      <div className="code-block-tabs">
        <button
          className={`tab-btn ${activeTab === 'program' ? 'active' : ''}`}
          onClick={() => setActiveTab('program')}
        >
          Program Blocks
          {generatedCode.program_blocks && generatedCode.program_blocks.length > 0 && (
            <span className="badge">{generatedCode.program_blocks.length}</span>
          )}
        </button>
        <button
          className={`tab-btn ${activeTab === 'function' ? 'active' : ''}`}
          onClick={() => setActiveTab('function')}
        >
          Functions
          {generatedCode.functions && generatedCode.functions.length > 0 && (
            <span className="badge">{generatedCode.functions.length}</span>
          )}
        </button>
        <button
          className={`tab-btn ${activeTab === 'function_block' ? 'active' : ''}`}
          onClick={() => setActiveTab('function_block')}
        >
          Function Blocks
          {generatedCode.function_blocks && generatedCode.function_blocks.length > 0 && (
            <span className="badge">{generatedCode.function_blocks.length}</span>
          )}
        </button>
      </div>

      {/* Tab Content */}
      <div className="code-block-content">
        {activeTab === 'program' && (
          <div className="program-blocks-section">
            {/* Global Labels - shown only once in program blocks tab */}
            <div className="code-section global-labels-section">
              <h4>🌐 Global Labels (Shared Across All Stages)</h4>
              {generatedCode.global_labels && generatedCode.global_labels.length > 0 ? (
                <div className="label-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Data Type</th>
                        <th>Class</th>
                        <th>Device</th>
                        <th>Initial Value</th>
                        <th>Comment</th>
                      </tr>
                    </thead>
                    <tbody>
                      {generatedCode.global_labels.map((label, i) => (
                        <tr key={i}>
                          <td>{label.name}</td>
                          <td>{label.data_type}</td>
                          <td>{label.class}</td>
                          <td>{label.device}</td>
                          <td>{label.initial_value || '-'}</td>
                          <td>{label.comment || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="no-data">No global labels</p>
              )}
            </div>

            {/* Program Blocks */}
            {generatedCode.program_blocks && generatedCode.program_blocks.length > 0 ? (
              generatedCode.program_blocks.map((block, index) => (
                <div key={index} className="program-block-item">
                  <div className="block-header">
                    <h4>Program Block {index + 1}</h4>
                  </div>
                  
                  {/* Program Metadata */}
                  <div className="block-metadata">
                    <div className="metadata-item">
                      <span className="label">Stage:</span>
                      <span className="value">{block.stage || 'N/A'}</span>
                    </div>
                    <div className="metadata-item">
                      <span className="label">Program Name:</span>
                      <span className="value">{block.name || 'N/A'}</span>
                    </div>
                    <div className="metadata-item">
                      <span className="label">Execution Type:</span>
                      <span className="value">{block.execution_type || 'Scan'}</span>
                    </div>
                  </div>

                  {/* Local Labels for this Program Block */}
                  <div className="code-section">
                    <h5>Local Labels</h5>
                    {block.local_labels && block.local_labels.length > 0 ? (
                      <div className="label-table">
                        <table>
                          <thead>
                            <tr>
                              <th>Name</th>
                              <th>Data Type</th>
                              <th>Class</th>
                              <th>Initial Value</th>
                            </tr>
                          </thead>
                          <tbody>
                            {block.local_labels.map((label, i) => (
                              <tr key={i}>
                                <td>{label.name}</td>
                                <td>{label.data_type}</td>
                                <td>{label.class}</td>
                                <td>{label.initial_value || '-'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <p className="no-data">No local labels</p>
                    )}
                  </div>

                  {/* Program Code */}
                  <div className="code-section">
                    <h5>Structured Text Code</h5>
                    <pre className="program-code">{block.code || 'No code generated'}</pre>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-blocks-message">
                <p>No program blocks generated</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'function' && (
          <div className="functions-section">
            {generatedCode.functions && generatedCode.functions.length > 0 ? (
              generatedCode.functions.map((func, index) => (
                <div key={index} className="function-item">
                  <div className="block-header">
                    <h4>⚡ Function {index + 1}</h4>
                  </div>
                  
                  {/* Function Metadata */}
                  <div className="block-metadata">
                    <div className="metadata-item">
                      <span className="label">Stage:</span>
                      <span className="value">{func.stage || 'N/A'}</span>
                    </div>
                    <div className="metadata-item">
                      <span className="label">Function Name:</span>
                      <span className="value">{func.name || 'N/A'}</span>
                    </div>
                    <div className="metadata-item">
                      <span className="label">With EN:</span>
                      <span className="value">{func.with_en ? 'Yes' : 'No'}</span>
                    </div>
                    <div className="metadata-item">
                      <span className="label">Result Type:</span>
                      <span className="value">{func.result_type || 'BOOL'}</span>
                    </div>
                  </div>

                  {/* Local Labels for this Function */}
                  <div className="code-section">
                    <h5>Local Labels</h5>
                    {func.local_labels && func.local_labels.length > 0 ? (
                      <div className="label-table">
                        <table>
                          <thead>
                            <tr>
                              <th>Name</th>
                              <th>Data Type</th>
                              <th>Class</th>
                              <th>Initial Value</th>
                            </tr>
                          </thead>
                          <tbody>
                            {func.local_labels.map((label, i) => (
                              <tr key={i}>
                                <td>{label.name}</td>
                                <td>{label.data_type}</td>
                                <td>{label.class}</td>
                                <td>{label.initial_value || '-'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <p className="no-data">No local labels</p>
                    )}
                  </div>

                  {/* Function Code */}
                  <div className="code-section">
                    <h5>Structured Text Code</h5>
                    <pre className="program-code">{func.code || 'No code generated'}</pre>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-blocks-message">
                <p>No functions generated</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'function_block' && (
          <div className="function-blocks-section">
            {generatedCode.function_blocks && generatedCode.function_blocks.length > 0 ? (
              generatedCode.function_blocks.map((fb, index) => (
                <div key={index} className="function-block-item">
                  <div className="block-header">
                    <h4>🔧 Function Block {index + 1}</h4>
                  </div>
                  
                  {/* Function Block Metadata */}
                  <div className="block-metadata">
                    <div className="metadata-item">
                      <span className="label">Stage:</span>
                      <span className="value">{fb.stage || 'N/A'}</span>
                    </div>
                    <div className="metadata-item">
                      <span className="label">Function Block Name:</span>
                      <span className="value">{fb.name || 'N/A'}</span>
                    </div>
                    <div className="metadata-item">
                      <span className="label">Type:</span>
                      <span className="value">{fb.fb_type || 'Subroutine Type'}</span>
                    </div>
                    <div className="metadata-item">
                      <span className="label">With EN:</span>
                      <span className="value">{fb.with_en ? 'Yes' : 'No'}</span>
                    </div>
                  </div>

                  {/* Local Labels for this Function Block */}
                  <div className="code-section">
                    <h5>Local Labels</h5>
                    {fb.local_labels && fb.local_labels.length > 0 ? (
                      <div className="label-table">
                        <table>
                          <thead>
                            <tr>
                              <th>Name</th>
                              <th>Data Type</th>
                              <th>Class</th>
                              <th>Initial Value</th>
                            </tr>
                          </thead>
                          <tbody>
                            {fb.local_labels.map((label, i) => (
                              <tr key={i}>
                                <td>{label.name}</td>
                                <td>{label.data_type}</td>
                                <td>{label.class}</td>
                                <td>{label.initial_value || '-'}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <p className="no-data">No local labels</p>
                    )}
                  </div>

                  {/* Function Block Code */}
                  <div className="code-section">
                    <h5>Structured Text Code</h5>
                    <pre className="program-code">{fb.code || 'No code generated'}</pre>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-blocks-message">
                <p>No function blocks generated</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default CodeBlockTabs;
