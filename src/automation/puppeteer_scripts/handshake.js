/**
 * Puppeteer script for automating Handshake message extraction
 */
const puppeteer = require('puppeteer');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

// Configuration
const HANDSHAKE_USERNAME = process.env.HANDSHAKE_USERNAME;
const HANDSHAKE_PASSWORD = process.env.HANDSHAKE_PASSWORD;
const MAX_MESSAGES = process.env.HANDSHAKE_MAX_MESSAGES || 10;
const HANDSHAKE_URL = 'https://app.joinhandshake.com/login';

/**
 * Main function to extract messages from Handshake
 */
async function extractHandshakeMessages() {
    // Validate credentials
    if (!HANDSHAKE_USERNAME || !HANDSHAKE_PASSWORD) {
        console.error('Missing Handshake credentials in environment variables');
        process.exit(1);
    }

    let browser;
    try {
        // Launch browser
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        const page = await browser.newPage();
        
        // Set a reasonable viewport
        await page.setViewport({ width: 1280, height: 800 });
        
        // Navigate to Handshake login page
        await page.goto(HANDSHAKE_URL, { waitUntil: 'networkidle2' });
        
        // Log in to Handshake
        await page.type('#email', HANDSHAKE_USERNAME);
        await page.type('#password', HANDSHAKE_PASSWORD);
        await Promise.all([
            page.click('input[name="commit"]'),
            page.waitForNavigation({ waitUntil: 'networkidle2' })
        ]);
        
        // Check if login was successful
        const currentUrl = page.url();
        if (currentUrl.includes('login') || currentUrl.includes('sign_in')) {
            throw new Error('Login to Handshake failed');
        }
        
        // Navigate to messages
        await page.waitForSelector('a[href*="/messages"]');
        await Promise.all([
            page.click('a[href*="/messages"]'),
            page.waitForNavigation({ waitUntil: 'networkidle2' })
        ]);
        
        // Wait for message threads to load
        await page.waitForSelector('.message-thread');
        
        // Extract message threads
        const messageThreads = await page.$$('.message-thread');
        console.log(`Found ${messageThreads.length} message threads`);
        
        // Process each thread up to the maximum
        const messages = [];
        for (let i = 0; i < Math.min(messageThreads.length, MAX_MESSAGES); i++) {
            // Click on the thread
            await messageThreads[i].click();
            
            // Wait for message content to load
            await page.waitForSelector('.message-content');
            
            // Extract the latest message
            const latestMessage = await page.evaluate(() => {
                const contents = document.querySelectorAll('.message-content');
                const senders = document.querySelectorAll('.message-sender');
                const timestamps = document.querySelectorAll('.message-timestamp');
                
                if (contents.length === 0) return null;
                
                const lastIndex = contents.length - 1;
                return {
                    id: `handshake_${Date.now()}`,
                    sender: senders[lastIndex] ? senders[lastIndex].textContent.trim() : 'Unknown Sender',
                    content: contents[lastIndex] ? contents[lastIndex].textContent.trim() : '',
                    timestamp: timestamps[lastIndex] ? timestamps[lastIndex].textContent.trim() : '',
                };
            });
            
            if (latestMessage) {
                messages.push(latestMessage);
            }
            
            // Go back to message list for next thread
            await Promise.all([
                page.click('a[href*="/messages"]'),
                page.waitForNavigation({ waitUntil: 'networkidle2' })
            ]);
            
            // Wait for message threads to load again
            await page.waitForSelector('.message-thread');
            
            // Re-fetch the message threads for the next iteration
            const updatedThreads = await page.$$('.message-thread');
            messageThreads[i+1] = updatedThreads[i+1];
        }
        
        // Output the messages as JSON
        console.log(JSON.stringify(messages));
        return messages;
        
    } catch (error) {
        console.error('Error in Puppeteer script:', error);
        process.exit(1);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Run the main function
extractHandshakeMessages(); 