# HARBOR Diamond Viewer - Static IP Configuration
# PowerShell script to set static IP on LattePanda WiFi adapter
# Run as Administrator

Write-Host "HARBOR Diamond Viewer - Static IP Configuration" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Get Wi-Fi adapter
$adapter = Get-NetAdapter | Where-Object {$_.Status -eq "Up" -and $_.Name -like "*Wi-Fi*"}

if ($adapter) {
    Write-Host "Found Wi-Fi adapter: $($adapter.Name)" -ForegroundColor Green
    
    # Prompt for static IP configuration
    $ipAddress = Read-Host "Enter desired static IP address (e.g., 192.168.1.100)"
    $subnet = Read-Host "Enter subnet mask (default: 255.255.255.0)"
    $gateway = Read-Host "Enter default gateway (e.g., 192.168.1.1)"
    $dns = Read-Host "Enter DNS server (e.g., 8.8.8.8)"
    
    if (!$subnet) { $subnet = "255.255.255.0" }
    if (!$dns) { $dns = "8.8.8.8" }
    
    Write-Host ""
    Write-Host "Configuring static IP..." -ForegroundColor Yellow
    
    try {
        # Remove existing IP configuration
        Remove-NetIPAddress -InterfaceAlias $adapter.Name -Confirm:$false -ErrorAction SilentlyContinue
        Remove-NetRoute -InterfaceAlias $adapter.Name -Confirm:$false -ErrorAction SilentlyContinue
        
        # Set static IP
        New-NetIPAddress -InterfaceAlias $adapter.Name -IPAddress $ipAddress -PrefixLength 24 -DefaultGateway $gateway
        
        # Set DNS
        Set-DnsClientServerAddress -InterfaceAlias $adapter.Name -ServerAddresses $dns
        
        Write-Host ""
        Write-Host "Success! Static IP configured:" -ForegroundColor Green
        Write-Host "  IP Address: $ipAddress" -ForegroundColor White
        Write-Host "  Subnet: $subnet" -ForegroundColor White
        Write-Host "  Gateway: $gateway" -ForegroundColor White
        Write-Host "  DNS: $dns" -ForegroundColor White
        Write-Host ""
        Write-Host "Mobile devices can now access:" -ForegroundColor Cyan
        Write-Host "  Control: http://$ipAddress:5000/control" -ForegroundColor White
        Write-Host "  Share: http://$ipAddress:5000/share" -ForegroundColor White
        
    } catch {
        Write-Host "Error: $_" -ForegroundColor Red
        Write-Host "Please run this script as Administrator" -ForegroundColor Yellow
    }
    
} else {
    Write-Host "Error: No active Wi-Fi adapter found" -ForegroundColor Red
    Write-Host "Please ensure Wi-Fi is enabled and connected" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
