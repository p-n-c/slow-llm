// API endpoint
const API_BASE_URL = 'http://127.0.0.1:5000'
let timerInterval = null
let startTime = null

// DOM elements
const systemPrompt = document.getElementById('system-prompt')
const singleUserPrompt = document.getElementById('single-user-prompt')
const sendSinglePromptBtn = document.getElementById('send-single-prompt')
const singleResponse = document.getElementById('single-response')
const requestTimer = document.getElementById('request-timer')

// Display model information
document.addEventListener('DOMContentLoaded', function () {
  if (window.SERVER_CONFIG) {
    document.getElementById('model-id').textContent =
      window.SERVER_CONFIG.DEFAULT_MODEL_ID
    document.getElementById('max-tokens').textContent =
      window.SERVER_CONFIG.MAX_TOKENS
  }
})

// Start timer function
function startTimer() {
  // Reset timer if it's already running
  if (timerInterval) {
    clearInterval(timerInterval)
  }

  // Set start time
  startTime = Date.now()

  // Update timer display every second with whole seconds only
  timerInterval = setInterval(() => {
    const elapsedTime = Math.floor((Date.now() - startTime) / 1000)
    requestTimer.textContent = `Response time: ${elapsedTime}s`
  }, 1000)
}

// Stop timer function
function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null

    // Calculate final elapsed time in whole seconds
    const elapsedTime = Math.floor((Date.now() - startTime) / 1000)
    requestTimer.textContent = `Response time: ${elapsedTime}s`
  }
}

// Send a single prompt
async function sendSinglePrompt() {
  const prompt = singleUserPrompt.value.trim()
  if (!prompt) return

  const system = systemPrompt.value.trim()

  sendSinglePromptBtn.disabled = true
  singleResponse.innerHTML =
    '<div class="message user-message"><strong>You:</strong> ' +
    prompt +
    '</div>'
  singleResponse.innerHTML +=
    '<div class="message model-message"><strong>Model:</strong> Loading...</div>'

  // Start the timer
  startTimer()

  try {
    const response = await fetch(`${API_BASE_URL}/prompt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: prompt,
        system: system || null,
      }),
    })

    const data = await response.json()

    // Stop the timer
    stopTimer()

    if (response.ok) {
      // Update the response text
      const messages = singleResponse.querySelectorAll('.message')
      const modelMessage = messages[messages.length - 1]
      modelMessage.innerHTML =
        '<strong>Model:</strong> ' + data.text.replace(/\n/g, '<br>')

      // Add usage information if available
      if (data.usage) {
        const usageInfo = document.createElement('div')
        usageInfo.className = 'usage-info'
        usageInfo.innerHTML = `<small>Input tokens: ${data.usage.input_tokens}, Output tokens: ${data.usage.output_tokens}</small>`
        modelMessage.appendChild(usageInfo)
      }
    } else {
      singleResponse.innerHTML +=
        '<div class="message model-message"><strong>Error:</strong> ' +
        data.error +
        '</div>'
    }
  } catch (error) {
    // Stop the timer
    stopTimer()

    console.error('Error sending prompt:', error)
    singleResponse.innerHTML +=
      '<div class="message model-message"><strong>Error:</strong> Failed to communicate with server</div>'
  } finally {
    sendSinglePromptBtn.disabled = false
  }
}

// Event listeners
sendSinglePromptBtn.addEventListener('click', sendSinglePrompt)

// Handle Enter key in single prompt
singleUserPrompt.addEventListener('keydown', function (event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendSinglePrompt()
  }
})
