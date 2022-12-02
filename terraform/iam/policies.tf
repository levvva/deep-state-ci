resource "aws_iam_policy" "eks_creators_policy" {
  name        = "eks_creators_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "sts:AssumeRole",
          "eks:CreateCluster",
          "eks:DeleteCluster",
          "eks:ListClusters",
          "eks:DescribeCluster",
          "ec2:Describe*",
          "ec2:AllocateAddress",
          "logs:CreateLogGroup",
          "ec2:CreateVpc",
          "ec2:DeleteVpc",
          "ec2:CreateTags",
          "ec2:CreateSecurityGroup",
          "ec2:CreateNatGateway",
          "ec2:DeleteSecurityGroup",
          "ec2:CreateInternetGateway",
          "ec2:CreateRouteTable",
          "ec2:RevokeSecurityGroupEgress",
          "ec2:ModifyVpcAttribute",
          "ec2:CreateSubnet",
          "ec2:DeleteSubnet",
          "ec2:AssociateRouteTable",
          "ec2:CreateNetworkInterface",
          "ec2:DeleteInternetGateway",
          "ec2:AuthorizeSecurityGroupEgress",
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:ModifySubnetAttribute",
          "ec2:CreateTags",
          "ec2:CreateRoute",
          "ec2:AttachInternetGateway",
          "logs:PutRetentionPolicy",
          "logs:DescribeLogGroups",
          "logs:DeleteLogGroup",
          "logs:ListTagsLogGroup"
        ]
        Effect   = "Allow"
        Resource = "*",
        "Condition": {
          "BoolIfExists": {
            "aws:MultiFactorAuthPresent": "true"
          },
          "StringEquals": {
            "aws:RequestedRegion": var.region
          }
        }
      },
      {
        Action = [
          "iam:GetRole",
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",
          "iam:UpdateAssumeRolePolicy",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePolicy",
          "iam:GetRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:PassRole",
          "iam:ListInstanceProfilesForRole"
        ]
        Effect   = "Allow"
        Resource = "*",
        "Condition": {
          "BoolIfExists": {
            "aws:MultiFactorAuthPresent": "true"
          }

        }
      },
    ]
  })
}

resource "aws_iam_role" "eks-cluster-creator" {
  name = "eks-cluster-creator"
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "EKSClusterAssumeRole",
        "Effect": "Allow",
        "Principal": {
          "AWS": "arn:aws:iam::067818091930:user/ekscreator",
          "Service": "eks.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  })
  inline_policy {
    name = "eks-cluster-creator-inline-policy"

    policy = jsonencode({
      "Version": "2012-10-17"
      "Statement": [
        {
          "Action": [
            "logs:CreateLogGroup"
          ],
          "Effect": "Deny",
          "Resource": "arn:aws:logs:${var.region}:${var.account_id}:log-group:/aws/eks/*/cluster"
        }
      ],
    })
  }

  tags = {
    tag-key = "tag-value"
  }
}


data "aws_iam_policy" "AmazonEKSClusterPolicy" {
  arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

data "aws_iam_policy" "AmazonEKSVPCResourceController" {
  arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
}

data "aws_iam_policy" "AmazonEKSServicePolicy" {
  arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
}

resource "aws_iam_role_policy_attachment" "eks-cluster-role-policy-attach" {
  role       = aws_iam_role.eks-cluster-creator.name
  policy_arn = data.aws_iam_policy.AmazonEKSClusterPolicy.arn
}

resource "aws_iam_role_policy_attachment" "eks-service-role-policy-attach" {
  role       = aws_iam_role.eks-cluster-creator.name
  policy_arn = data.aws_iam_policy.AmazonEKSServicePolicy.arn
}

resource "aws_iam_role_policy_attachment" "eks-vpc-resource-role-policy-attach" {
  role       = aws_iam_role.eks-cluster-creator.name
  policy_arn = data.aws_iam_policy.AmazonEKSVPCResourceController.arn
}
