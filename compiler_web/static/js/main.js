// Initialize CodeMirror
const editor = CodeMirror.fromTextArea(document.getElementById('codeInput'), {
    mode: 'text/x-c',
    theme: 'monokai',
    lineNumbers: true,
    autoCloseBrackets: true,
    matchBrackets: true,
    indentUnit: 4,
    tabSize: 4,
    lineWrapping: true,
    extraKeys: {
        'Tab': 'indentMore',
        'Shift-Tab': 'indentLess'
    }
});

// Theme handling
let isDarkMode = false;
const themeToggle = document.getElementById('themeToggle');

themeToggle.addEventListener('click', () => {
    isDarkMode = !isDarkMode;
    document.body.classList.toggle('dark-mode');
});

// AST Visualization
function displayAST(astString) {
    const container = document.getElementById('astVisualization');
    container.style.height = 'auto';
    container.innerHTML = `<pre class="ast-tree">${astString}</pre>`;
}

// Output handling
function updateOutput(output) {
    const codeOutput = document.getElementById('codeOutput');
    console.log('Updating output:', output);  // Debug log
    
    if (Array.isArray(output) && output.length > 0) {
        // Filter out any null or undefined values
        const validOutput = output.filter(line => line != null);
        if (validOutput.length > 0) {
            codeOutput.textContent = validOutput.join('\n');
            console.log('Valid output:', validOutput);  // Debug log
        } else {
            codeOutput.textContent = '(No valid output)';
            console.log('No valid output lines');  // Debug log
        }
    } else {
        codeOutput.textContent = '(No output)';
        console.log('No output array or empty array');  // Debug log
    }
    
    // Ensure the output is visible
    codeOutput.style.display = 'block';
    codeOutput.scrollIntoView({ behavior: 'smooth' });
}

// Compile button handler
document.getElementById('compileBtn').addEventListener('click', async () => {
    const code = editor.getValue();
    const codeOutput = document.getElementById('codeOutput');
    codeOutput.textContent = 'Compiling...';  // Show compilation in progress
    
    try {
        const response = await fetch('/compile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code })
        });
        
        const data = await response.json();
        console.log('Compile response:', data);  // Debug log
        
        if (data.success) {
            // Update AST visualization
            displayAST(data.ast);
            
            // Update tokens table
            const tokensBody = document.querySelector('#tokensTable tbody');
            tokensBody.innerHTML = data.tokens.map(token => `
                <tr>
                    <td>${token.type}</td>
                    <td>${token.value}</td>
                </tr>
            `).join('');
            
            // Update IR code
            const irCode = document.getElementById('irCode');
            if (data.ir_code) {
                irCode.textContent = Array.isArray(data.ir_code) ? 
                    data.ir_code.join('\n') : 
                    data.ir_code;
            }
            
            // Update target code
            const targetCode = document.getElementById('targetCode');
            if (data.target_code) {
                targetCode.textContent = Array.isArray(data.target_code) ? 
                    data.target_code.join('\n') : 
                    data.target_code;
            }
            
            // Update output and switch to output tab
            updateOutput(data.output);
            const outputTab = document.querySelector('[href="#outputTab"]');
            const tab = new bootstrap.Tab(outputTab);
            tab.show();
        } else {
            showError(data.error || 'Compilation failed');
        }
    } catch (error) {
        console.error('Compilation error:', error);  // Debug log
        showError(error.message || 'An error occurred during compilation');
    }
});

// Load example button handler
document.getElementById('loadExampleBtn').addEventListener('click', () => {
    const exampleCode = `int main() {
    int x = 5;
    int y = 10;
    int z = x + y * 2;
    
    // Test if-else
    if (z > 20) {
        print("z is greater than 20");
        x = x + 1;
    } else {
        print("z is 20 or less");
        y = y - 1;
    }
    
    // Test while loop
    while (x < y) {
        x = x + 1;
        print(x);
    }
    
    return 0;
}`;
    editor.setValue(exampleCode);
});

// Clear button handler
document.getElementById('clearBtn').addEventListener('click', () => {
    editor.setValue('');
});

// Copy buttons handlers
document.getElementById('copyIrBtn').addEventListener('click', () => {
    copyToClipboard(document.getElementById('irCode').textContent);
});

document.getElementById('copyTargetBtn').addEventListener('click', () => {
    copyToClipboard(document.getElementById('targetCode').textContent);
});

// Download AST button handler
document.getElementById('downloadAstBtn').addEventListener('click', () => {
    if (network) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const pixelRatio = window.devicePixelRatio;
        const dimensions = network.getBoundingBox();
        const width = dimensions.right - dimensions.left + 50;
        const height = dimensions.bottom - dimensions.top + 50;
        
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';
        canvas.width = width * pixelRatio;
        canvas.height = height * pixelRatio;
        
        ctx.scale(pixelRatio, pixelRatio);
        network.fit();
        
        const dataUrl = canvas.toDataURL();
        const link = document.createElement('a');
        link.download = 'ast.png';
        link.href = dataUrl;
        link.click();
    }
});

// Utility functions
function showError(message) {
    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
    document.getElementById('errorMessage').textContent = message;
    errorModal.show();
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Could add a toast notification here
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
} 