resource "aws_iam_policy" "eks_creators_policy" {
  name        = "eks_creators_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "eks:CreateCluster",
          "eks:ListClusters"
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
    ]
  })
}
