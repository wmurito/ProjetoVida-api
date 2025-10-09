# Script para verificar configuração VPC

$SecurityGroupId = "sg-010ebae9343e8f422"
$SubnetId1 = "subnet-0fcb4e5a4433397c3"
$SubnetId2 = "subnet-045bdd15a0355fdbc"

Write-Host "🔍 Verificando configuração VPC..." -ForegroundColor Cyan

# 1. Verificar Security Group
Write-Host "`n1️⃣ Security Group Rules:" -ForegroundColor Yellow
aws ec2 describe-security-groups --group-ids $SecurityGroupId --query 'SecurityGroups[0].{Inbound:IpPermissions,Outbound:IpPermissionsEgress}' --output json

# 2. Verificar Subnets
Write-Host "`n2️⃣ Subnet 1 Info:" -ForegroundColor Yellow
aws ec2 describe-subnets --subnet-ids $SubnetId1 --query 'Subnets[0].{SubnetId:SubnetId,VpcId:VpcId,AvailabilityZone:AvailabilityZone,CidrBlock:CidrBlock,MapPublicIpOnLaunch:MapPublicIpOnLaunch}' --output table

Write-Host "`n3️⃣ Subnet 2 Info:" -ForegroundColor Yellow
aws ec2 describe-subnets --subnet-ids $SubnetId2 --query 'Subnets[0].{SubnetId:SubnetId,VpcId:VpcId,AvailabilityZone:AvailabilityZone,CidrBlock:CidrBlock,MapPublicIpOnLaunch:MapPublicIpOnLaunch}' --output table

# 3. Obter VPC ID
$VpcId = aws ec2 describe-subnets --subnet-ids $SubnetId1 --query 'Subnets[0].VpcId' --output text

# 4. Verificar Route Tables
Write-Host "`n4️⃣ Route Tables:" -ForegroundColor Yellow
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$VpcId" --query 'RouteTables[*].{RouteTableId:RouteTableId,Routes:Routes[*].[DestinationCidrBlock,GatewayId,NatGatewayId]}' --output json

# 5. Verificar NAT Gateways
Write-Host "`n5️⃣ NAT Gateways:" -ForegroundColor Yellow
aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=$VpcId" --query 'NatGateways[*].{NatGatewayId:NatGatewayId,State:State,SubnetId:SubnetId}' --output table

# 6. Verificar Internet Gateway
Write-Host "`n6️⃣ Internet Gateway:" -ForegroundColor Yellow
aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=$VpcId" --query 'InternetGateways[*].{InternetGatewayId:InternetGatewayId,State:Attachments[0].State}' --output table

Write-Host "`n✅ Verificação concluída!" -ForegroundColor Green

Write-Host "`n📋 Checklist:" -ForegroundColor Cyan
Write-Host "  [ ] Security Group permite saída para 0.0.0.0/0 porta 443 (HTTPS)" -ForegroundColor Gray
Write-Host "  [ ] Security Group permite saída para RDS porta 5432" -ForegroundColor Gray
Write-Host "  [ ] Subnets têm NAT Gateway OU são públicas com Internet Gateway" -ForegroundColor Gray
Write-Host "  [ ] Route Table tem rota 0.0.0.0/0 → NAT Gateway ou Internet Gateway" -ForegroundColor Gray
