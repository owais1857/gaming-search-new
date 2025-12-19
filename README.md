#  Personalized Context-Aware Gaming Search

Welcome! This is the complete guide to setting up and running the full-stack, privacy-focused search engine for the gaming community. We've built this project to deliver smart, personalized results without ever tracking you.

Let's get started!



### . Install All Dependencies**

1.  **Open a PowerShell terminal** and navigate to the main project folder:
    
    
2.  **Set up the Python Virtual Environment:** This creates a clean, isolated space for our backend libraries.
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```
    

3.  **Install the Backend's Python Libraries:**
    
    pip install -r requirements.txt
    

4.  **Install the Frontend's JavaScript Libraries:**
    
    cd frontend
    npm install
    
You're all set up!



## Part 2: Running the Project for a Demo

 It involves collecting data, updating the search engine's "brain," and then launching the application.

### **Stage 1: Gather Some Fresh Data**

Let's run our crawlers to get the latest content from the web.

1.  Make sure your `venv` is active. From the main project folder, navigate to the `crawler` directory:
    
  2.  Run the crawlers one by one. These commands will **add** new data to your files without deleting the old content.
    ```powershell
    # Run Scrapy Spiders
    scrapy crawl ign_news -o ign_news_deep.json -s FEED_OVERWRITE=False
    scrapy crawl gamespot_news -o gamespot_news.json -s FEED_OVERWRITE=False
    scrapy crawl workwithindies_jobs -o workwithindies_jobs.json -s FEED_OVERWRITE=False

    # Run Python Scripts
    python reddit_news.py
    python gaming_crawler/spiders/general_crawler.py
    ```

### **Stage 2: Update the Search Engine's "Brain"**

Now, let's process all that new data and make it searchable.

1.  Make sure your `venv` is active. From the main project folder, navigate to the `nlp_pipeline` directory:
    
2.  Run these three scripts **in order**. This is a crucial step!
    ```powershell
    # 1. Consolidates all data and removes duplicates
    python 1_consolidate_data.py

    # 2. Creates AI embeddings for the new data
    python 2_generate_embeddings.py

    # 3. Builds the final, searchable index file
    python 3_build_index.py
    ```

### **Stage 3: Launch the Application!**

It's time to bring it all to life. For this, you'll need **two separate PowerShell terminals**.

#### **Terminal 1: Start the Backend**

1.  Open a new terminal.
2.  Navigate to the project folder and activate the environment:
    ```powershell
    .\venv\Scripts\activate
    ```
3.  Go to the `backend` folder and start the server:
    ```powershell
    cd backend
    python app.py
    ```
4.  You'll see a message that the server is running. **Leave this terminal open!**

#### **Terminal 2: Start the Frontend**

1.  Open a **second, new** terminal.
2.  Navigate directly to the `frontend` folder:
    
3.  Start the React application:
    ```powershell
    npm start
    ```

A browser window will pop up at `http://localhost:3000`. Your personalized gaming search engine is now live and ready to use!
