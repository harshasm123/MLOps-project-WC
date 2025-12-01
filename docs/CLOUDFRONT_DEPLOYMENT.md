# CloudFront Deployment Guide

## Overview

CloudFront provides global content delivery for your MLOps Platform frontend with:
- **Global Edge Locations** - Faster loading worldwide
- **HTTPS by Default** - Secure connections
- **Caching** - Reduced server load and faster response times
- **Compression** - Automatic gzip compression
- **Security Headers** - Built-in security policies

## Deployment Options

### Option 1: Add CloudFront to Existing Deployment

```bash
# Deploy infrastructure with CloudFront
./deploy.sh --cloudfront

# Or full deployment with CloudFront
./deploy.sh --full-cloudfront
```

### Option 2: Standalone CloudFront Deployment

```bash
# Deploy only CloudFront (requires existing backend)
./deploy-cloudfront.sh
```

### Option 3: Manual CloudFormation

```bash
# Deploy CloudFront stack
aws cloudformation deploy \
  --template-file infrastructure/cloudfront-template.yaml \
  --stack-name mlops-platform-cloudfront-dev \
  --parameters \
    ParameterKey=Environment,ParameterValue=dev \
    ParameterKey=FrontendBucketName,ParameterValue=mlops-platform-frontend-dev-123456789012

# Upload frontend assets
aws s3 sync frontend/build/ s3://mlops-platform-frontend-dev-123456789012/ --delete

# Invalidate cache
aws cloudfront create-invalidation \
  --distribution-id E1234567890123 \
  --paths "/*"
```

## Features

### Caching Strategy
- **Static Assets** (`/static/*`): 1 year cache
- **HTML Files**: No cache (always fresh)
- **API Calls**: No cache (dynamic content)

### Security
- **HTTPS Only**: All HTTP redirected to HTTPS
- **Security Headers**: HSTS, X-Frame-Options, etc.
- **Origin Access Control**: S3 bucket only accessible via CloudFront

### Performance
- **HTTP/2**: Faster multiplexed connections
- **IPv6**: Modern internet protocol support
- **Compression**: Automatic gzip for text files
- **Edge Locations**: 400+ locations worldwide

## Usage

After deployment, your frontend will be available at:
```
https://d1234567890123.cloudfront.net
```

### Update Frontend
```bash
# Build and deploy updates
cd frontend
npm run build
cd ..

# Upload to S3
aws s3 sync frontend/build/ s3://your-frontend-bucket/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

### Monitor Performance
```bash
# View CloudFront metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name Requests \
  --dimensions Name=DistributionId,Value=YOUR_DISTRIBUTION_ID \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

## Cost Optimization

- **Price Class 100**: US, Canada, Europe only (cheapest)
- **Static Asset Caching**: Reduces origin requests
- **Compression**: Reduces data transfer costs

Estimated cost: $1-5/month for typical usage.

## Cleanup

```bash
# Delete CloudFront stack
aws cloudformation delete-stack --stack-name mlops-platform-cloudfront-dev

# Empty and delete S3 bucket
aws s3 rm s3://your-frontend-bucket --recursive
aws s3 rb s3://your-frontend-bucket
```