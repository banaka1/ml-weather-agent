### 1. 配置Git全局用户名（关联GitHub账号）
git config --global user.name "你的GitHub用户名"

### 2. 配置Git全局邮箱（关联GitHub绑定邮箱）
git config --global user.email "你的GitHub绑定邮箱"

### 3. （可选）增大Git HTTP推送缓存（解决大文件/网络波动推送失败）
git config --global http.postBuffer 524288000

### 4. （可选，网络不通时）配置Git代理（与浏览器代理一致，示例端口7890）
### HTTP/HTTPS代理（最常用）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

### （备选）SOCKS5协议代理（部分代理工具使用）
git config --global http.proxy socks5://127.0.0.1:7890
git config --global https.proxy socks5://127.0.0.1:7890

### 5. （可选）取消Git全局代理（推送成功后如需清理）
git config --global --unset http.proxy
git config --global --unset https.proxy


# 二、 本地仓库初始化与提交（项目根目录执行）
### 1. 初始化本地Git仓库（首次使用时执行，生成.git文件夹）
git init

### 2. 查看本地Git状态（确认文件跟踪情况，排错常用）
git status

### 3. 添加所有未被忽略的文件到暂存区（. 代表所有文件）
git add .

### 4. 提交暂存区文件到本地仓库（-m 后必须跟提交描述，清晰易懂）
git commit -m "Initial commit: 项目初始化，完善.gitignore忽略无用文件"

# 远程仓库关联
### 1. 查看当前远程仓库关联状态（验证是否关联、别名是否正确）
git remote -v

### 2. （若别名错误/关联错误）删除旧的远程仓库关联（示例：删除错误别名origi）
git remote rm origi

### 3. 关联GitHub远程仓库（替换为自己的仓库HTTPS地址，别名设为标准origin）
git remote add origin https://github.com/你的GitHub用户名/你的仓库名.git

### 4. （可选）本地分支重命名（若旧分支是master，想改为main，适配GitHub默认分支）
git branch -M main

# 四、 核心推送操作（本地→GitHub 远程仓库）

### 1. 首次推送（建立本地分支与远程分支跟踪关系，-u 后续可简化命令）
#### 场景A：本地分支是master（本次操作使用）
git push -u origin master

#### 场景B：本地分支是main（GitHub默认新分支）
git push -u origin main

#### 场景C：远程别名是错误的origi（临时应急使用）
git push -u origi master

### 2. 后续推送（已建立跟踪关系，直接简化命令，无需重复写完整路径）
git push

# 五、 后续完善项目（添加 README/License 等）
### 1. 添加新文件（如README.md）到暂存区
git add README.md LICENSE

### 2. 提交新文件到本地仓库
git commit -m "完善开源项目：添加README说明书和MIT许可证"

### 3. 推送到GitHub远程仓库（简化命令，已建立跟踪）
git push

# 补充：常用辅助命令（排错 / 查询）

### 1. 查看本地所有分支
git branch

### 2. 查看Git全局配置清单（验证用户名、代理、缓存是否生效）
git config --global --list

### 3. 查看提交历史（确认本地提交记录）
git log

