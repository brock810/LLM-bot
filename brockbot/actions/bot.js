const bp = require('botpress');


const axios = require('axios');

bp.hear(/(.*)/, async (event, next) => {

  const userInput = event.text;

  try {
    const response = await axios.post('http://127.0.0.1:8087/generate', {
      prompt: userInput,
      temperature: 1.0, 
    });

    const generatedCode = response.data.completion;

    await bp.cms.renderElement(event.channel, 'builtin_text', { text: generatedCode });

  } catch (error) {
    console.error('Error:', error.message);
    await bp.cms.renderElement(event.channel, 'builtin_text', { text: 'An error occurred while generating code.' });
  }

  next();
});