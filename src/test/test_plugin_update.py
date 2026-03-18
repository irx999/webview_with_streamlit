#!/usr/bin/env python3
"""
插件更新功能测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.manager.plugins_manager import Plugins_Manager


def test_plugin_update():
    """测试插件更新功能"""
    manager = Plugins_Manager()
    
    # 测试插件名称和GitHub仓库
    plugin_name = "ps_of_py"
    github_repo = "irx999/ps_of_py"  # 请根据实际仓库地址修改
    
    print(f"正在测试插件 {plugin_name} 的更新功能...")
    print(f"GitHub仓库: {github_repo}")
    
    # 检查是否有更新
    print("\n1. 检查更新...")
    has_update = manager.check_for_updates(plugin_name, github_repo)
    print(f"是否有更新: {has_update}")
    
    if has_update:
        print("\n2. 执行更新...")
        success = manager.update_plugin(plugin_name, github_repo)
        print(f"更新结果: {'成功' if success else '失败'}")
    else:
        print("\n2. 跳过更新（已是最新版本）")
    
    print("\n测试完成！")


if __name__ == "__main__":
    test_plugin_update()