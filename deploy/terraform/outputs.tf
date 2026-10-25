output "asg_name" {
  value       = aws_autoscaling_group.asg.name
  description = "Name of the Inoculated PHP Auto-Scaling Group"
}

output "launch_template_id" {
  value       = aws_launch_template.inoculated_template.id
  description = "ID of the Inoculated Launch Template"
}

output "security_group_id" {
  value       = aws_security_group.web_sg.id
  description = "ID of the Web Security Group"
}
