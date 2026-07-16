# =========================================================================
# INPUT VARIABLES
# =========================================================================

variable "ses_sender_email" {
  description = "Verified SES email address for sending alerts"
  type        = string
}

variable "manager_email" {
  description = "Warehouse manager email to receive alerts"
  type        = string
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "gemini_api_key" {
  description = "Google Gemini API key for AI recommendations"
  type        = string
  sensitive   = true
}
