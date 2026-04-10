# Migrating Zomato AI Database to Neon

To allow your Streamlit Cloud deployment to access your database, we need to move from your local PostgreSQL (`localhost`) to a managed serverless cloud database like Neon. Neon gives you a free, instantly provisioned Postgres database that is completely compatible with our setup.

Follow these 5 simple steps to migrate:

### Step 1: Create a Neon Database
1. Go to [Neon.tech](https://neon.tech/) and sign up for a free account.
2. Click **Create Project**.
3. Name your project (e.g., `Zomato AI`) and your database (e.g., `zomato`).
4. Select a region closest to your users.
5. Once created, you will see your **Connection String**. It will look something like this:
   `postgresql://neondb_owner:YOUR_PASSWORD@ep-nameless-sun-12345.us-east-2.aws.neon.tech/zomato?sslmode=require`

### Step 2: Update Your Local `.env`
Update your local environment variables so your ingestion pipeline knows where to send the data.
1. Open the `.env` file at the root of your project.
2. Replace the `POSTGRES_DSN` variable with your new Neon connection string:
   ```env
   POSTGRES_DSN=postgresql://neondb_owner:YOUR_PASSWORD@ep-nameless-sun-12345.us-east-2.aws.neon.tech/zomato?sslmode=require
   ```

### Step 3: Run the Data Pipeline
Currently, your Neon database is empty and has no tables. Luckily, your project's data ingestion script automatically creates the `restaurants` schema and loads all the Hugging Face data for you!

Open your terminal in the root folder and run:
```bash
python -m data_pipeline.ingest_zomato
```
*Note: This will download the Zomato AI dataset and directly inject thousands of records into your Neon Cloud database. It may take a minute or two.*

### Step 4: Configure Streamlit Cloud Secrets
Now that your database is hosted on the cloud and populated with data, you just need to explicitly give Streamlit permission to access it.
1. Go to your app dashboard at [share.streamlit.io](https://share.streamlit.io/).
2. Click the `⋮` (three dots) next to your app, and select **Settings**.
3. Go to the **Secrets** tab.
4. Add your database connection string and your Groq API key:
   ```toml
   POSTGRES_DSN = "postgresql://neondb_owner:YOUR_PASSWORD@ep-nameless-sun-12345.us-east-2.aws.neon.tech/zomato?sslmode=require"
   GROQ_API_KEY = "gsk_xxxxxxx"
   ```
5. Click **Save**.

### Step 5: Test Your Cloud App
Reboot your Streamlit Cloud app. It will securely read `POSTGRES_DSN` from the Streamlit Secrets, connect to your new Neon serverless database, pull the live restaurant candidates, and run them seamlessly through the LLM!
