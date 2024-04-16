class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        }

        this.state = false;
        this.messages = [];
    }

    display() {
        const {openButton, chatBox, sendButton} = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox))

        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }

    toggleState(chatbox) {
        this.state = !this.state;

        // show or hides the box
        if(this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value
        if (text1 === "") {
            return;
        }

        let msg1 = { name: "User", message: text1 }
        this.messages.push(msg1);

        fetch($SCRIPT_ROOT+'/predict', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
              'Content-Type': 'application/json'
            },
          })
          .then(r => r.json())
          .then(r => {
            let msg2 = { name: "Sam", message: r.answer };
            this.messages.push(msg2);
            this.updateChatText(chatbox)
            textField.value = ''

        }).catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbox)
            textField.value = ''
          });
    }

    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function(item, index) {
            if (item.name === "Sam") {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'
            } else {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
            }
        });
    
        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    
        // Add code to prompt user for feedback
        if (this.messages.length > 0 && this.messages[this.messages.length - 1].name === "Sam") {
            const feedbackPrompt = document.createElement('div');
            feedbackPrompt.innerHTML = '<div class="messages__item messages__item--operator">How satisfied are you with the response? <button class="feedback-button" id="satisfiedButton">Satisfied</button> <button class="feedback-button" id="unsatisfiedButton">Unsatisfied</button></div>';
            chatmessage.appendChild(feedbackPrompt);
    
            // Add event listeners to the satisfaction feedback buttons
            const satisfiedButton = document.getElementById('satisfiedButton');
            const unsatisfiedButton = document.getElementById('unsatisfiedButton');
    
            satisfiedButton.addEventListener('click', () => sendFeedback('satisfied'));
            unsatisfiedButton.addEventListener('click', () => sendFeedback('unsatisfied'));
        }
    }
    
   sendFeedback(feedback) 
   {
        // Send feedback to Flask backend
        fetch($SCRIPT_ROOT + '/feedback', {
            method: 'POST',
            body: JSON.stringify({ feedback: feedback }),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(r => r.json())
        .then(r => {
            // Handle response from backend
            if (feedback === 'satisfied') {
                // If user is satisfied, hide chatbox
                const chatbox = document.querySelector('.chatbox__support');
                chatbox.classList.remove('chatbox--active');
            } else {
                // If user is unsatisfied, display further assistance options
                const chatmessage = document.querySelector('.chatbox__messages');
                const furtherAssistance = document.createElement('div');
                furtherAssistance.innerHTML = '<div class="messages__item messages__item--operator">We apologize for any inconvenience. How can we assist you further?</div>';
                chatmessage.appendChild(furtherAssistance);
            }
        }).catch((error) => {
            console.error('Error:', error);
        });
    }
}
const chatbox = new Chatbox();
chatbox.display();