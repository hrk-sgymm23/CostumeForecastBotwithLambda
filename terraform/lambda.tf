# locals {
#     lambda_function_name = "costume_forecast_bot"
#     iam_role_name_lambda = "lambda_role"
#     iam_policy_name_lambda = "lambda_policy"
# }

# # lambdaソースコードをzip化する処理
# # locals {
# #     source_files = [
# #         "./src/lambda_function.py",
# #         "./src/module.py",
# #     ]
# # }

# # output "template_file" {
# #   value = [for idx, file in local.source_files : {
# #     index    = idx
# #     contents = templatefile("${path.module}/templates/${file}", {})
# #   }]
# # }

# # # Lambda                                                                       #
# # data "archive_file" "archive" {
# #   type        = "zip"
# # #   source_dir  = "../src/lambda_function"
# #   source {
# #     filename = "${basename(local.source_files[0])}"
# #     content = "${data.template_file.t_file.0.rendered}"
# #   }
# #   source {
# #     filename = "${basename(local.source_files[1])}"
# #     content = "${data.template_file.t_file.1.rendered}"
# #   }
# #   output_path = "./src_file/costume_bot.zip"
# # }

# data "archive_file" "function" {
#   type        = "zip"
#   source_dir  = "../src"
#   output_path = "../outputs/zipfile/src.zip"
# }

# resource "aws_lambda_layer_version" "lambda_layer" {
#   # layerは手動でzip化
#   filename   = "../tweet_bot.zip"
#   layer_name = "costume_bot_layer"

#   compatible_runtimes = ["python3.10"]
# }

# resource "aws_lambda_function" "costume_forecast" {
#   function_name    = local.lambda_function_name
#   filename = data.archive_file.function.output_path
#   role             = aws_iam_role.iam_for_lambda.arn
#   handler          = "lambda_function.lambda_handler"
#   source_code_hash = data.archive_file.function.output_base64sha256
#   runtime          = "python3.10"

#   layers = [aws_lambda_layer_version.lambda_layer.arn]
# }

# data "aws_iam_policy_document" "assume_role" {
#   statement {
#     effect = "Allow"

#     principals {
#       type        = "Service"
#       identifiers = ["lambda.amazonaws.com"]
#     }

#     actions = ["sts:AssumeRole"]
#   }
# }

# resource "aws_iam_role" "iam_for_lambda" {
#   name               = "iam_for_lambda"
#   assume_role_policy = data.aws_iam_policy_document.assume_role.json
# }


