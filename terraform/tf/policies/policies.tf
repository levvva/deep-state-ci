resource "aws_iam_policy" "policy" {
  name        = "DemoUserEks"
  path        = "/"
  description = "My test policy"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "eks:CreateCluster",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}