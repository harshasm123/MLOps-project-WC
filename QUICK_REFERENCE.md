# Quick Reference Card

## 🚀 Deploy in 3 Commands

```bash
chmod +x prereq.sh deploy-complete.sh
./prereq.sh                    # Check dependencies
./deploy-complete.sh           # Deploy everything
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `prereq.sh` | Check all dependencies |
| `deploy-complete.sh` | Deploy all 3 pipelines |
| `SAGEMAKER_EXECUTION_GUIDE.md` | How code runs automatically |
| `GITOPS_GUIDE.md` | GitHub deployment |
| `FINAL_SUMMARY.md` | Complete overview |

## 🎯 How It Works

**NO JUPYTER NOTEBOOK!** Code runs automatically:

```
UI Button Click → Lambda → SageMaker → Model Trained
```

## 💻 Test Locally (Optional)

```bash
pip install -r requirements.txt
python3 -c "from src.pipelines.training_pipeline import TrainingPipeline; print('Works!')"
```

## 📊 Monitor

```bash
# View logs
aws logs tail /aws/lambda/mlops-platform-training-handler-dev --follow

# List jobs
aws sagemaker list-training-jobs --max-results 10
```

## 🐛 Troubleshoot

```bash
# Check stack
aws cloudformation describe-stacks --stack-name mlops-platform-dev

# Check function
aws lambda get-function --function-name mlops-platform-training-handler-dev
```

## 💰 Cost

- **Dev**: $35-85/month
- **Prod**: $160-450/month

## ✅ Checklist

- [ ] Run `./prereq.sh`
- [ ] Run `./deploy-complete.sh`
- [ ] Access UI
- [ ] Start training
- [ ] View results

**That's it!** 🎉
