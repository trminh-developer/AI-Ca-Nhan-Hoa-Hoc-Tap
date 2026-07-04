FROM node:18-alpine

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy file cấu hình package và cài đặt dependencies
COPY package*.json ./
RUN npm ci

# Copy toàn bộ mã nguồn
COPY . .

# Build ứng dụng Next.js
RUN npm run build

# Mở port 3000
EXPOSE 3000

# Lệnh khởi chạy frontend
CMD ["npm", "start"]
