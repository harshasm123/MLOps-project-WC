# SageMaker Execution Guide

## How Python Files Run Automatically in SageMaker

**NO JUPYTER NOTEBOOK NEEDED!** The Python files run automatically as SageMaker jobs triggered by Lambda functions.

---

## 🎯 Execution Flow

```
User/API Request
        ↓
Lambda Function (training_handler.py)
        ↓
Creates SageMaker Training Job
        ↓
SageMaker automatically:
  1. Provisions compute (ml.m5.xlarge)
  2. Downloads your code from S3
  3. Runs training_pipeline.py
  4. Saves model to S3
  5. Shuts down compute
        ↓
Model registered in Model Registry
```

**You never touch a Jupyter notebook!** Everything is automated.

---

## 📋 How It Works

### 1. Lambda Triggers SageMaker

When you call the API or click "Start Training" in the UI:

```python
# backend/lambda/training_handler.py
def lambda_handler(event, context):
    # Lambda creates a SageMaker training job
    response = sagemaker.create_training_job(
        TrainingJobName='medication-adherence-20241129',
        AlgorithmSpecification={
            'TrainingImage': 'sagemaker-scikit-learn-image',
            'TrainingInputMode': 'File'
        },
        InputDataConfig=[{
            'ChannelName': 'training',
            'DataSource': {
                'S3DataSource': {
                    'S3Uri': 's3://bucket/diabetic_data.csv'
                }
            }
        }],
        OutputDataConfig={
            'S3OutputPath': 's3://bucket/models/'
        }
    )
```

### 2. SageMaker Runs Your Code

SageMaker automatically:

1. **Provisions compute** - Spins up ml.m5.xlarge instance
2. **Downloads data** - Gets diabetic_data.csv from S3
3. **Runs your script** - Executes `src/pipelines/training_pipeline.py`
4. **Saves output** - Uploads model to S3
5. **Cleans up** - Shuts down instance

### 3. Your Code Executes

```python
# src/pipelines/training_pipeline.py
if __name__ == "__main__":
    # SageMaker sets these paths automatically
    data_path = '/opt/ml/input/data/training/train.csv'
    output_path = '/opt/ml/model/'
    
    # Your training code runs
    pipeline = TrainingPipeline(config)
    result = pipeline.execute(data_path, output_path)
    
    # SageMaker uploads everything in /opt/ml/model/ to S3
```

---

## 🚀 Three Ways to Run

### Method 1: Via React UI (Easiest)

1. Open the React UI
2. Go to "Training Pipeline" tab
3. Fill in form:
   - Dataset URI: `s3://bucket/diabetic_data.csv`
   - Model Name: `medication-adherence-model`
   - Algorithm: `RandomForest`
4. Click "Start Training"

**What happens:**
- UI calls API Gateway
- API Gateway triggers Lambda
- Lambda creates SageMaker job
- SageMaker runs `training_pipeline.py`
- Model saved to S3
- UI shows completion

### Method 2: Via API (Programmatic)

```bash
curl -X POST https://your-api.amazonaws.com/prod/training/start \
  -H "Content-Type: application/json" \
  -d '{
    "datasetUri": "s3://bucket/diabetic_data.csv",
    "modelName": "medication-adherence-model",
    "algorithm": "RandomForest",
    "instanceType": "ml.m5.xlarge"
  }'
```

### Method 3: Via AWS Console (Manual)

1. Go to SageMaker console
2. Click "Training jobs"
3. Click "Create training job"
4. Configure and start

**But you don't need to do this!** Methods 1 & 2 are automated.

---

## 📁 SageMaker Directory Structure

When your code runs in SageMaker, it has this structure:

```
/opt/ml/
├── input/
│   └── data/
│       └── training/
│           └── train.csv          # Your input data
├── model/                          # Save your model here
│   ├── model.joblib               # SageMaker uploads this to S3
│   ├── features.json
│   └── baseline_statistics.json
├── code/                           # Your Python code
│   └── training_pipeline.py
└── output/                         # Logs and metrics
```

**Key paths:**
- Input data: `/opt/ml/input/data/training/`
- Save model: `/opt/ml/model/`
- Your code: `/opt/ml/code/`

---

## 🔄 Complete Training Flow

### Step-by-Step Execution

```
1. User clicks "Start Training" in UI
        ↓
2. React app calls API Gateway
   POST /training/start
        ↓
3. API Gateway triggers Lambda
   training_handler.py
        ↓
4. Lambda creates SageMaker training job
   {
     TrainingJobName: "job-20241129-123456",
     AlgorithmSpecification: {...},
     InputDataConfig: [...],
     OutputDataConfig: {...}
   }
        ↓
5. SageMaker provisions ml.m5.xlarge instance
   (takes ~2-3 minutes)
        ↓
6. SageMaker downloads:
   - Your code from S3
   - Training data from S3
        ↓
7. SageMaker runs:
   python3 training_pipeline.py
        ↓
8. Your code executes:
   - Load data
   - Preprocess
   - Train model
   - Evaluate
   - Save to /opt/ml/model/
        ↓
9. SageMaker uploads /opt/ml/model/ to S3
   s3://bucket/models/job-20241129-123456/
        ↓
10. Lambda registers model in DynamoDB
    {
      version: "v1.0.0",
      metrics: {...},
      status: "completed"
    }
        ↓
11. UI shows "Training Complete!"
    Displays metrics and model version
```

---

## 🎓 Inference Flow (Similar)

```
1. User clicks "Run Inference" in UI
        ↓
2. Lambda creates SageMaker batch transform job
        ↓
3. SageMaker runs inference_pipeline.py
        ↓
4. Predictions saved to S3
        ↓
5. UI displays results
```

---

## 💻 Local Testing (Optional)

You CAN test locally before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Test training pipeline
python3 -c "
from src.pipelines.training_pipeline import TrainingPipeline

config = {'algorithm': 'RandomForest', 'n_estimators': 100}
pipeline = TrainingPipeline(config)
result = pipeline.execute('diabetic_data.csv', 'models/')
print(f'Training completed: {result.status}')
"

# Test inference pipeline
python3 -c "
from src.pipelines.inference_pipeline import InferencePipeline

pipeline = InferencePipeline('models/', 'models/baseline_statistics.json')
result = pipeline.execute('test_data.csv', 'predictions/')
print(f'Predictions: {result.prediction_count}')
"
```

But this is **optional** - you can deploy directly to SageMaker!

---

## 🔍 Monitoring Execution

### View Training Job Status

**Via UI:**
- Go to "Training Pipeline" tab
- See job status in real-time

**Via AWS Console:**
1. Go to SageMaker console
2. Click "Training jobs"
3. Find your job
4. View logs in CloudWatch

**Via CLI:**
```bash
# List training jobs
aws sagemaker list-training-jobs --max-results 10

# Describe specific job
aws sagemaker describe-training-job \
  --training-job-name medication-adherence-20241129

# View logs
aws logs tail /aws/sagemaker/TrainingJobs \
  --follow \
  --filter-pattern medication-adherence
```

---

## 🐛 Debugging

### If Training Fails

1. **Check CloudWatch Logs:**
```bash
aws logs tail /aws/sagemaker/TrainingJobs --follow
```

2. **Check Lambda Logs:**
```bash
aws logs tail /aws/lambda/mlops-platform-training-handler-dev --follow
```

3. **Check SageMaker Job:**
```bash
aws sagemaker describe-training-job \
  --training-job-name <job-name>
```

### Common Issues

**Issue: "No module named 'src'"**
- **Fix**: Ensure `src/` is packaged correctly
- Lambda should upload code to S3 before starting job

**Issue: "File not found: train.csv"**
- **Fix**: Check S3 URI in request
- Verify data exists: `aws s3 ls s3://bucket/diabetic_data.csv`

**Issue: "Out of memory"**
- **Fix**: Use larger instance type
- Change `instanceType` to `ml.m5.2xlarge`

---

## 📊 Cost Breakdown

### Training Job Cost

```
Instance: ml.m5.xlarge
Rate: $0.269/hour
Training time: ~10 minutes
Cost per training: $0.045

Monthly (10 trainings): $0.45
```

### Inference Job Cost

```
Instance: ml.t2.medium
Rate: $0.065/hour
Inference time: ~5 minutes
Cost per inference: $0.005

Monthly (100 inferences): $0.50
```

**Total ML compute: ~$1/month for development**

---

## 🎯 Key Takeaways

1. **✅ NO Jupyter Notebook Needed**
   - Everything runs automatically via Lambda + SageMaker

2. **✅ Fully Automated**
   - Click button in UI → Model trained → Results displayed

3. **✅ Scalable**
   - SageMaker handles compute provisioning
   - Auto-scales based on demand

4. **✅ Cost-Effective**
   - Pay only for compute time used
   - Instances shut down automatically

5. **✅ Production-Ready**
   - Same code runs in dev and prod
   - No manual intervention needed

---

## 🚀 Quick Start

```bash
# 1. Check prerequisites
chmod +x prereq.sh
./prereq.sh

# 2. Deploy infrastructure
./deploy-complete.sh

# 3. Open UI
open frontend/build/index.html

# 4. Click "Start Training"
# That's it! SageMaker runs your code automatically.
```

---

## 📚 Additional Resources

- **SageMaker Training**: https://docs.aws.amazon.com/sagemaker/latest/dg/how-it-works-training.html
- **SageMaker Inference**: https://docs.aws.amazon.com/sagemaker/latest/dg/how-it-works-inference.html
- **Lambda + SageMaker**: https://docs.aws.amazon.com/lambda/latest/dg/services-sagemaker.html

---

**Your Python code runs automatically in SageMaker - no Jupyter notebooks required!** 🎉
