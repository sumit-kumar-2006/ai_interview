import os

for root, dirs, files in os.walk('database'):
    print(root, files)

for root, dirs, files in os.walk('backend'):
    print(root, files)
