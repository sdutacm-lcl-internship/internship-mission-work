# 如何从指定分支检出新分支？

```zsh
# 切换到指定分支
git checkout source-branch
# 创建并检出新分支
git checkout -b new-branch
```

# git add 是 add 文件到哪里去？没有 add 的文件是否会被 commit 包含？

## git add 是添加文件到哪里？

git add 命令用于将文件添加到Git的暂存区（Staging Area）。暂存区是一个中间区域，它保存了即将提交到仓库的文件快照。通过git add命令，你可以选择性地将工作目录中的更改添加到暂存区，以准备进行下一次提交。

## 没有 git add 的文件是否会被 commit 包含？

没有经过 git add 的文件更改不会被包含在提交（commit）中。只有那些已经被添加到暂存区的文件才会在提交时被记录下来。

# 如果 master 更新了，你的分支要如何对齐它的更新？

```zsh
# 切换到你的分支上
git checkout feature-branch
# 获取最新的 master 分支更新
git fetch origin
# 合并 master 到你的分支上
git merge origin/master
# 或者使用 rebase，将你的分支的提交应用在master分支的最新提交之上，从而保持线性历史
git rebase origin
# 如果出现冲突需要解决冲突，手动解决冲突之后，继续 rebase
git rebase --continue
```
