FROM mcr.microsoft.com/dotnet/sdk:3.1
RUN dotnet tool install -g mlnet
ENV PATH="$PATH:/root/.dotnet/tools"
