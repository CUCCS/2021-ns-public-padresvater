# 基于 VirtualBox 的网络攻防基础环境搭建

[toc]

## 实验目的

- 掌握 VirtualBox 虚拟机的安装与使用；
- 掌握 VirtualBox 的虚拟网络类型和按需配置；
- 掌握 VirtualBox 的虚拟硬盘多重加载；

## 实验环境

- VirtualBox 虚拟机  版本 6.1.18 r142142 (Qt5.6.2)
- 攻击者主机（Attacker）：Kali  2021.2（多重加载）
- 网关（Gateway, GW）：Debian10 Buster
- 靶机（Victim）： 两个Windows xp-sp3 ，一个kali 2021.2

## 实验要求完成情况

### 虚拟硬盘配置成多重加载

如下图所示；

![多重加载](.\img\多重加载.png)

![多重加载结果](.\img\多重加载结果.png)



### 搭建虚拟机的网络拓扑



- |              网关端口               |      IP      |
  | :---------------------------------: | :----------: |
  |           NAT(连接攻击者)           |   10.0.2.6   |
  |      intnet1（连接xp-victim）       | 172.16.111.1 |
  | intnet2(连接xp2=victim,kali-victim) | 172.16.222.1 |

  

  

- |   hostname    |       IP       |
  | :-----------: | :------------: |
  | kali-attacker |   10.0.2.15    |
  |   xp-victim   | 172.16.111.101 |
  |  xp2-victim   | 172.16.222.149 |
  |  kali-victim  | 172.16.222.144 |

  

### 网络连通性测试

- [x] 靶机可以直接访问攻击者主机

  - intnet2下的kali靶机访问攻击者主机

    ![靶机3ping攻击者](.\img\靶机3ping攻击者.png)

  - intnet2下的xp靶机访问攻击者主机

    ![xp2ping攻击者](.\img\xp2ping攻击者.png)

  - intnet1下的xp靶机访问攻击者主机

    ![xp1ping攻击者](.\img\xp1ping攻击者.png)

  

- [x] 攻击者主机无法直接访问靶机

  - 攻击者ping  intnet1下的xp靶机

    ![攻击者pingxp1](.\img\攻击者pingxp1.png)

  - 攻击者ping  intnet2下的xp靶机

    ![攻击者pingxp2](.\img\攻击者pingxp2.png)

  - 攻击者ping  intnet2下的kali靶机

    ![攻击者ping靶机](.\img\攻击者ping靶机.png)

- [x] 网关可以直接访问攻击者主机和靶机

  - 网关访问攻击者

    ![网关ping攻击者](.\img\网关ping攻击者.png)

  - 网关访问靶机

    ![网关ping靶机1](.\img\网关ping靶机1.png)

    ![网关ping靶机2](.\img\网关ping靶机2.png)

    

- [x] 靶机的所有对外上下行流量必须经过网关

  - 两个抓包文件：[intnet1.pcap](./pcap/intnet1.pcap)   [intnet2.pcap](./pcap/intnet2.pcap) 

  - intnet2下靶机的对外流量经过网关：

    ![流量监控2](.\img\流量监控2.png)

  - intnet1下靶机的对外流量经过网关：

    ![监听1](.\img\监听1.png)

- [x] 所有节点均可以访问互联网

- [ ] - intnet1下的xp靶机ping互联网

    ![靶机1ping互联网](.\img\靶机1ping互联网.png)

  - intnet2下的xp靶机ping互联网

    ![靶机2ping互联网](.\img\靶机2ping互联网.png)

  - intnet2下的kali靶机ping互联网

    ![靶机3ping互联网](.\img\靶机3ping互联网.png)

  - 攻击者ping互联网

    ![攻击者ping互联网](.\img\攻击者ping互联网.png)



## 实验流程

### 配置网关（Debian10）

![gateway](.\img\gateway.png)

详情如下：

- enp0s3（）

![netcard1](.\img\netcard1.png)

- enp0s8(便于使用ssh远程连接)

![netcard2](.\img\netcard2.png)

- enp0s9

![netcard1](.\img\netcard3.png)

- enp0s10

![netcard1](.\img\netcard4.png)

其中host-only的设置如下：

![netcard1](.\img\hostonly-conf.png)

#### 测试SSH连接

![ssh](.\img\ssh.png)

#### 更改网关网络配置文件

- 输入命令``` sudo vi /etc/network/interfaces ```

- 粘贴

```
# /etc/network/interfaces
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
allow-hotplug enp0s3
iface enp0s3 inet dhcp
  post-up iptables -t nat -A POSTROUTING -s 172.16.111.0/24 ! -d 172.16.0.0/16 -o enp0s3 -j MASQUERADE
  post-up iptables -t nat -A POSTROUTING -s 172.16.222.0/24 ! -d 172.16.0.0/16 -o enp0s3 -j MASQUERADE

  # demo for DNAT
  post-up iptables -t nat -A PREROUTING -p tcp -d 192.168.56.113 --dport 80 -j DNAT --to-destination 172.16.111.118
  post-up iptables -A FORWARD -p tcp -d '172.16.111.118' --dport 80 -j ACCEPT
  
  post-up iptables -P FORWARD DROP
  post-up iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
  post-up iptables -A FORWARD -s '172.16.111.0/24' ! -d '172.16.0.0/16' -j ACCEPT
  post-up iptables -A FORWARD -s '172.16.222.0/24' ! -d '172.16.0.0/16' -j ACCEPT
  post-up iptables -I INPUT -s 172.16.111.0/24 -d 172.16.222.0/24 -j DROP
  post-up iptables -I INPUT -s 172.16.222.0/24 -d 172.16.111.0/24 -j DROP
  post-up echo 1 > /proc/sys/net/ipv4/ip_forward
  post-down echo 0 > /proc/sys/net/ipv4/ip_forward
  post-down iptables -t nat -F
  post-down iptables -F
allow-hotplug enp0s8
iface enp0s8 inet dhcp
allow-hotplug enp0s9
iface enp0s9 inet static
  address 172.16.111.1
  netmask 255.255.255.0
allow-hotplug enp0s10
iface enp0s10 inet static
  address 172.16.222.1
  netmask 255.255.255.0
```

- 重启虚拟机

- 输入```ip a```查看网卡设置

  ```
  2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
      link/ether 08:00:27:f2:1c:0a brd ff:ff:ff:ff:ff:ff
      inet 10.0.2.6/24 brd 10.0.2.255 scope global dynamic enp0s3
         valid_lft 523sec preferred_lft 523sec
      inet6 fe80::a00:27ff:fef2:1c0a/64 scope link
         valid_lft forever preferred_lft forever
         
  3: enp0s8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
      link/ether 08:00:27:4f:89:d4 brd ff:ff:ff:ff:ff:ff
      inet 192.168.56.113/24 brd 192.168.56.255 scope global dynamic enp0s8
         valid_lft 523sec preferred_lft 523sec
      inet6 fe80::a00:27ff:fe4f:89d4/64 scope link
         valid_lft forever preferred_lft forever
         
  4: enp0s9: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
      link/ether 08:00:27:91:42:ff brd ff:ff:ff:ff:ff:ff
      inet 172.16.111.1/24 brd 172.16.111.255 scope global enp0s9
         valid_lft forever preferred_lft forever
      inet6 fe80::a00:27ff:fe91:42ff/64 scope link
         valid_lft forever preferred_lft forever
         
  5: enp0s10: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
      link/ether 08:00:27:8e:47:84 brd ff:ff:ff:ff:ff:ff
      inet 172.16.222.1/24 brd 172.16.222.255 scope global enp0s10
         valid_lft forever preferred_lft forever
      inet6 fe80::a00:27ff:fe8e:4784/64 scope link
         valid_lft forever preferred_lft forever
  ```

  接下来配置自启动dnsmasq

  安装dnsmasq以后按要求修改```/etc/dnsmasq.d```中的相关设置

  输入```systemctl enable dnsmasq```开启自启动

  #### 流量监控

  - ```apt update && apt install tmux``` 便于后台操作
  - ``` apt install tcpdump``` 
  - ```tcpdump -i enp0s10 -n -w intnet2.pcap``` 抓包（通过intnet2网卡的流量）
  - 随意浏览几个网页
  - 将抓包文件通过scp传输到宿主机上查看

### 配置靶机网络

- xp的网络控制芯片不支持1000M，须选择PCnet-Fast

- xp-victim (172.16.111.101) -----  intnet1 (enp0s9 172.16.111.1)

  

- xp2-victim (172.16.222.149)  /   kali-victim(172.16.222.144) ----- intnet2 (enp0s10 172.16.222.1 )

### 配置攻击者网络

- 使用“NAT网络”
- ip 为 10.0.2.15

## 遇到的问题与解决方法

- 远程ssh登录有permission denied的问题，经过搜索得知是由于root用户权限问题，默认无法使用ssh远程登录root用户。

  解决方法是找到默认配置文件sshd_config，将```PermitRootLogin``` 后的值改为```yes```，取消注释即可。



