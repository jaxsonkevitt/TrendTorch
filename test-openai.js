const dotenv = require('dotenv');
const path = require('path');
const { OpenAI } = require('openai');

console.log('Script started');

const envPath = path.join(__dirname, '.env.local');
console.log('Loading .env.local from:', envPath);

dotenv.config({ path: envPath });

console.log('OPENAI_API_KEY:', process.env.OPENAI_API_KEY ? 'Set' : 'Not set');

const openai = new OpenAI(process.env.OPENAI_API_KEY);

async function testOpenAI() {
  console.log('Testing OpenAI API...');
  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [{ role: "user", content: "Hello, can you hear me?" }],
    });

    console.log("OpenAI API test successful!");
    console.log("Response:", completion.choices[0].message.content);
  } catch (error) {
    console.error("OpenAI API test failed:");
    console.error(error);
  }
}

testOpenAI();

console.log('Script ended');
