resource "aws_iam_policy" "eks_creators_policy" {
  name        = "eks_creators_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "eks:CreateCluster",
          "eks:DeleteCluster",
          "eks:ListClusters",
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
