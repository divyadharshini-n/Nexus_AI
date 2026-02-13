// Parse Structured Text code to extract labels
export const parseLabelsFromCode = (code) => {
  const globalLabels = [];
  const localLabels = [];
  
  if (!code) return { globalLabels, localLabels };
  
  const lines = code.split('\n');
  let inGlobalVars = false;
  let inLocalVars = false;
  
  for (let line of lines) {
    const trimmedLine = line.trim();
    
    // Check for VAR_GLOBAL section
    if (trimmedLine.startsWith('VAR_GLOBAL')) {
      inGlobalVars = true;
      inLocalVars = false;
      continue;
    }
    
    // Check for VAR section (local variables)
    if (trimmedLine.startsWith('VAR') && !trimmedLine.startsWith('VAR_GLOBAL')) {
      inLocalVars = true;
      inGlobalVars = false;
      continue;
    }
    
    // End of variable declaration section
    if (trimmedLine === 'END_VAR') {
      inGlobalVars = false;
      inLocalVars = false;
      continue;
    }
    
    // Parse variable declarations
    if ((inGlobalVars || inLocalVars) && trimmedLine && !trimmedLine.startsWith('//')) {
      const labelMatch = trimmedLine.match(/^(\w+)\s*:\s*(\w+)(?:\s*:=\s*(.+?))?(?:\s*;\s*\/\/\s*(.+))?/);
      
      if (labelMatch) {
        const [, name, dataType, initialValue, comment] = labelMatch;
        
        const label = {
          name: name,
          data_type: dataType,
          class: '',
          initial_value: initialValue ? initialValue.replace(';', '').trim() : '',
          comment: comment ? comment.trim() : ''
        };
        
        if (inGlobalVars) {
          // Try to extract device address from comment or name
          const deviceMatch = (comment || name).match(/([XYMDT]\d+)/i);
          label.device = deviceMatch ? deviceMatch[1] : '';
          label.class = 'Global';
          globalLabels.push(label);
        } else if (inLocalVars) {
          label.class = 'Local';
          localLabels.push(label);
        }
      }
    }
  }
  
  return { globalLabels, localLabels };
};

// Format labels back to Structured Text format
export const formatLabelsToCode = (globalLabels, localLabels) => {
  let code = '';
  
  // Format global variables
  if (globalLabels && globalLabels.length > 0) {
    code += 'VAR_GLOBAL\n';
    globalLabels.forEach(label => {
      let line = `    ${label.name} : ${label.data_type}`;
      if (label.initial_value) {
        line += ` := ${label.initial_value}`;
      }
      line += ';';
      if (label.comment || label.device) {
        line += ' //';
        if (label.device) line += ` ${label.device}`;
        if (label.comment) line += ` ${label.comment}`;
      }
      code += line + '\n';
    });
    code += 'END_VAR\n\n';
  }
  
  // Format local variables
  if (localLabels && localLabels.length > 0) {
    code += 'VAR\n';
    localLabels.forEach(label => {
      let line = `    ${label.name} : ${label.data_type}`;
      if (label.initial_value) {
        line += ` := ${label.initial_value}`;
      }
      line += ';';
      if (label.comment) {
        line += ` // ${label.comment}`;
      }
      code += line + '\n';
    });
    code += 'END_VAR\n\n';
  }
  
  return code;
};

export default {
  parseLabelsFromCode,
  formatLabelsToCode
};
