resource "aws_iam_group" "eks_creators_group" {
  name = "eks_creators"
}



resource "aws_iam_group_policy_attachment" "eks_creators_group_policy_attachment" {
  group      = aws_iam_group.eks_creators_group.name
  policy_arn = aws_iam_policy.eks_creators_policy.arn
}
