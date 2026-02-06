output "public_ip" {
  value = aws_instance.nebulus.public_ip
}

output "instance_id" {
  value = aws_instance.nebulus.id
}
