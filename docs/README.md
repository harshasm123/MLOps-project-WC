# MLOps Platform Documentation

Complete documentation for the MLOps Platform - Medication Adherence Prediction System.

## 📖 Table of Contents

### Getting Started

- **[QUICKSTART.md](QUICKSTART.md)** - Get up and running in minutes
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Detailed step-by-step deployment guide
- **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - Overview of the deployment process
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Common commands and quick operations

### Architecture & Design

- **[COMPLETE_ARCHITECTURE.md](COMPLETE_ARCHITECTURE.md)** - Full system architecture with diagrams
- **[AWS_WELL_ARCHITECTED.md](AWS_WELL_ARCHITECTED.md)** - AWS Well-Architected Framework alignment
- **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** - Complete project overview and summary

### ML Operations

- **[SAGEMAKER_EXECUTION_GUIDE.md](SAGEMAKER_EXECUTION_GUIDE.md)** - Running training and inference jobs on SageMaker
  - Training pipeline execution
  - Inference pipeline execution
  - Model registry operations
  - Monitoring and drift detection

### CI/CD & GitOps

- **[GITOPS_GUIDE.md](GITOPS_GUIDE.md)** - Complete GitOps workflow with GitHub Actions
  - GitHub Actions setup
  - Automated testing and deployment
  - Branch protection and workflows
  
- **[GITOPS_VS_CODECOMMIT.md](GITOPS_VS_CODECOMMIT.md)** - Why we chose GitOps over CodeCommit
  - Migration rationale
  - Comparison of approaches
  - Benefits and trade-offs

### Frontend Hosting

- **[AMPLIFY_DEPLOYMENT_GUIDE.md](AMPLIFY_DEPLOYMENT_GUIDE.md)** - AWS Amplify deployment guide
  - Amplify setup and configuration
  - Automatic CI/CD from GitHub
  - Custom domain setup
  
- **[UI_HOSTING_SUMMARY.md](UI_HOSTING_SUMMARY.md)** - Frontend hosting options comparison
  - Amplify vs CloudFront
  - Cost analysis
  - Feature comparison

## 🗂️ Document Categories

### For First-Time Users
1. Start with [QUICKSTART.md](QUICKSTART.md)
2. Review [COMPLETE_ARCHITECTURE.md](COMPLETE_ARCHITECTURE.md)
3. Follow [DEPLOYMENT.md](DEPLOYMENT.md)

### For Developers
1. Review [GITOPS_GUIDE.md](GITOPS_GUIDE.md)
2. Check [SAGEMAKER_EXECUTION_GUIDE.md](SAGEMAKER_EXECUTION_GUIDE.md)
3. Reference [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### For DevOps Engineers
1. Study [AWS_WELL_ARCHITECTED.md](AWS_WELL_ARCHITECTED.md)
2. Review [GITOPS_GUIDE.md](GITOPS_GUIDE.md)
3. Check [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)

### For Architects
1. Read [COMPLETE_ARCHITECTURE.md](COMPLETE_ARCHITECTURE.md)
2. Review [AWS_WELL_ARCHITECTED.md](AWS_WELL_ARCHITECTED.md)
3. Check [FINAL_SUMMARY.md](FINAL_SUMMARY.md)

## 🔗 Related Resources

### Specification Documents
Located in `../.kiro/specs/mlops-platform/`:
- **requirements.md** - Feature requirements with acceptance criteria
- **design.md** - Technical design with correctness properties
- **tasks.md** - Implementation task breakdown

### Infrastructure Code
Located in `../infrastructure/`:
- **cloudformation-template.yaml** - Main infrastructure
- **cicd-pipeline.yaml** - CI/CD pipeline
- **data-pipeline.yaml** - Data processing pipeline
- **frontend-hosting.yaml** - Amplify hosting configuration
- **gitops-config.yaml** - GitOps configuration

### Source Code
Located in `../src/`:
- **pipelines/** - Training and inference pipelines
- **models/** - Data models and schemas
- **monitoring/** - Drift detection and monitoring
- **registry/** - Model registry operations

## 📝 Documentation Standards

All documentation follows these principles:
- **Clear and concise** - No unnecessary jargon
- **Step-by-step** - Easy to follow instructions
- **Code examples** - Practical, runnable examples
- **Diagrams** - Visual representations where helpful
- **Up-to-date** - Reflects current implementation

## 🤝 Contributing to Documentation

When updating documentation:
1. Keep the same format and style
2. Update this index if adding new documents
3. Cross-reference related documents
4. Include code examples where applicable
5. Test all commands and procedures

## 📧 Support

For questions or issues:
1. Check the relevant documentation first
2. Review the [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
3. Consult the specification documents
4. Check AWS CloudWatch logs for runtime issues

---

**Last Updated**: November 2025  
**Version**: 1.0  
**Project**: MLOps Platform - Medication Adherence Prediction
