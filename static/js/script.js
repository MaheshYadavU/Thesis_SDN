document.getElementById('prompt-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const prompt = document.getElementById('prompt').value;
    
    fetch('/generate-code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('code-output').innerText = data.code;
        document.getElementById('response').classList.remove('hidden');
        
        // Update the execute button's onclick event
        document.getElementById('execute-code').onclick = function() {
            fetch('/execute-code', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('execution-result').innerText = data.message;
            })
            .catch(error => console.error('Error:', error));
        };
    })
    .catch(error => console.error('Error:', error));
});


