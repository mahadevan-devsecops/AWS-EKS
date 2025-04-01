1. Create IAM Policy
    aws iam create-policy --policy-name AWSLoadBalancerControllerIAMPolicy --policy-document file://iam_policy.json
     Output is 
{
    "Policy": {
        "PolicyName": "AWSLoadBalancerControllerIAMPolicy",
        "PolicyId": "ANPA45Y2RUSYLHJX3AZ46",
        "Arn": "arn:aws:iam::888577041584:policy/AWSLoadBalancerControllerIAMPolicy",
        "Path": "/",
        "DefaultVersionId": "v1",
        "AttachmentCount": 0,
        "PermissionsBoundaryUsageCount": 0,
        "IsAttachable": true,
        "CreateDate": "2025-03-31T03:55:38+00:00",
        "UpdateDate": "2025-03-31T03:55:38+00:00"
    }
}
2. Create IAM OIDC provider
    eksctl utils associate-iam-oidc-provider --region=us-east-1 --cluster=thenextgensolutions --approve

2. Attach IAM Role to EKS, Retrive the policy arn from the above step.
    eksctl create iamserviceaccount --cluster thenextgensolutions --namespace kube-system --name aws-load-balancer-controller --attach-policy-arn arn:aws:iam::888577041584:policy/AWSLoadBalancerControllerIAMPolicy --approve
6. Add the following tag in the subnet, 
    Retrive the VPC ID
    aws eks describe-cluster --name thenextgensolutions --region us-east-1 --query "cluster.resourcesVpcConfig.subnetIds"

        [
            "subnet-01b15f37c2ffbc53f",
            "subnet-032e6d8f3850f7516"
        ]

    Add Tag to the subnets
    aws ec2 create-tags --resources subnet-032e6d8f3850f7516 subnet-01b15f37c2ffbc53f --tags Key=kubernetes.io/role/elb,Value=1

4. Create Load Balancer
    kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller/crds?ref=master"
    
    Install Helm 
        winget install Helm.Helm

    Add and Install Helm Chart 
        helm repo add eks https://aws.github.io/eks-charts
        helm repo update
        helm install ws-load-balancer-controller eks/aws-load-balancer-controller  -n kube-system  --set clusterName=thenextgensolutions


5. Install Deployment, Service and Ingress
    kubectl apply -f manifest\order-service.yaml
    kubectl apply -f manifest\order-ingress.yaml