/**
 * Utility functions for Puppeteer scripts
 */

/**
 * Wait for an element to be visible and return it
 * @param {Object} page - Puppeteer page object
 * @param {string} selector - CSS selector to find
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Promise<Object>} - Element handle
 */
async function waitForElement(page, selector, timeout = 10000) {
    await page.waitForSelector(selector, { visible: true, timeout });
    return page.$(selector);
}

/**
 * Safely click on an element
 * @param {Object} page - Puppeteer page object
 * @param {string} selector - CSS selector to click
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Promise<boolean>} - Success status
 */
async function safeClick(page, selector, timeout = 10000) {
    try {
        const element = await waitForElement(page, selector, timeout);
        if (!element) {
            return false;
        }
        
        // Check if element is visible and clickable
        const isVisible = await page.evaluate(el => {
            const rect = el.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0;
        }, element);
        
        if (!isVisible) {
            return false;
        }
        
        // Try regular click
        await element.click();
        return true;
    } catch (error) {
        // Try JavaScript click as fallback
        try {
            await page.evaluate(selector => {
                const element = document.querySelector(selector);
                if (element) element.click();
            }, selector);
            return true;
        } catch (jsError) {
            return false;
        }
    }
}

/**
 * Fill a form with the provided data
 * @param {Object} page - Puppeteer page object
 * @param {Object} formData - Form data mapping selectors to values
 * @returns {Promise<boolean>} - Success status
 */
async function fillForm(page, formData) {
    try {
        for (const [selector, value] of Object.entries(formData)) {
            await page.waitForSelector(selector);
            await page.click(selector, { clickCount: 3 }); // Triple click to select all existing text
            await page.type(selector, value);
        }
        return true;
    } catch (error) {
        return false;
    }
}

/**
 * Wait for navigation to complete
 * @param {Object} page - Puppeteer page object
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Promise<boolean>} - Success status
 */
async function waitForPageLoad(page, timeout = 30000) {
    try {
        await page.waitForNavigation({ 
            waitUntil: ['domcontentloaded', 'networkidle2'],
            timeout 
        });
        return true;
    } catch (error) {
        return false;
    }
}

/**
 * Extract text from an element
 * @param {Object} page - Puppeteer page object
 * @param {string} selector - CSS selector
 * @returns {Promise<string>} - Extracted text
 */
async function extractText(page, selector) {
    try {
        await page.waitForSelector(selector);
        return page.evaluate(selector => {
            const element = document.querySelector(selector);
            return element ? element.textContent.trim() : '';
        }, selector);
    } catch (error) {
        return '';
    }
}

/**
 * Take a screenshot for debugging
 * @param {Object} page - Puppeteer page object
 * @param {string} name - Screenshot name
 */
async function takeScreenshot(page, name) {
    await page.screenshot({ 
        path: `screenshots/${name}_${Date.now()}.png`,
        fullPage: true 
    });
}

// Export all utilities
module.exports = {
    waitForElement,
    safeClick,
    fillForm,
    waitForPageLoad,
    extractText,
    takeScreenshot
}; 