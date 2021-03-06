---
title: iaas-paas-saas
date: 2016-7-22 22:37:00
tags: [iaas,paas,saas]
---
### 转自：[http://hi.baidu.com/www100/blog/item/81ff10172dd7b00f4a90a703.html](http://hi.baidu.com/www100/blog/item/81ff10172dd7b00f4a90a703.html)
- iaas paas saas 三种服务模式
>- 它们之间的关系主要可以从两个角度进行分析：其一是用户体验角度，从这个角度而言，它们之间关系是独立的，因为它们面对不同类型的用户。其二是技术角度，从这个角度而言，它们并不是简单的继承关系 
>- 三种服务模式
根据现在最常用，也是比较权威的NIST(National Institute of Standards and Technology，美国国家标准技术研究院)定义，云计算主要分为三种服务模式，而且这个三层的分法重要是从用户体验的角度出发的：
Software as a Service，软件即服务，简称SaaS，这层的作用是将应用作为服务提供给客户。
Platform as a Service，平台即服务，简称PaaS，这层的作用是将一个开发平台作为服务提供给用户。
Infrastructure as a Service， 基础设施即服务，简称IaaS，这层的作用是提供虚拟机或者其他资源作为服务提供给用户。 

>>- 一、SaaS模式 
>>>- 作用
通过SaaS这种模式，用户只要接上网络，并通过浏览器，就能直接使用在云端上运行的应用，而不需要顾虑类似安装等琐事，并且免去初期高昂的软硬件投入。SaaS主要面对的是普通的用户。
>>>- 产品
主要产品包括：Salesforce Sales Cloud，Google Apps，Zimbra，Zoho和IBM Lotus Live等。
>>>- 功能
谈到SaaS的功能，也可以认为是要实现SaaS服务，供应商需要完成那些功能?主要有四个方面：
随时随地访问：在任何时候或者任何地点，只要接上网络，用户就能访问这个SaaS服务。
支持公开协议：通过支持公开协议(比如HTML4/5)，能够方便用户使用。
安全保障：SaaS供应商需要提供一定的安全机制，不仅要使存储在云端的用户数据处于绝对安全的境地，而且也要在客户端实施一定的安全机制(比如HTTPS)来保护用户。
多住户(Multi-Tenant)机制：通过多住户机制，不仅能更经济地支撑庞大的用户规模，而且能提供一定的可定制性以满足用户的特殊需求。
>>- 二、PaaS模式
>>>- 作用
通过PaaS这种模式，用户可以在一个包括SDK，文档和测试环境等在内的开发平台上非常方便地编写应用，而且不论是在部署，或者在运行的时候，用户都无需为服务器，操作系统，网络和存储等资源的管理操心，这些繁琐的工作都由PaaS供应商负责处理，而且PaaS在整合率上面非常惊人，比如一台运行Google App Engine的服务器能够支撑成千上万的应用，也就是说，PaaS是非常经济的。PaaS主要的用户是开发人员。
>>>- 产品
主要产品包括：Google App Engine，force.com，heroku和Windows Azure Platform等。
>>>- 功能
为了支撑着整个PaaS平台的运行，供应商需要提供那么功能?主要有四大功能：
友好的开发环境：通过提供SDK和IDE等工具来让用户能在本地方便地进行应用的开发和测试。
丰富的服务：PaaS平台会以API的形式将各种各样的服务提供给上层的应用。自动的资源调度：也就是可伸缩这个特性，它将不仅能优化系统资源，而且能自动调整资源来帮助运行于其上的应用更好地应对突发流量。精细的管理和监控：通过PaaS能够提供应用层的管理和监控，比如，能够观察应用运行的情况和具体数值(比如，吞吐量和反映时间)来更好地衡量应用的运行状态，还有能够通过精确计量应用使用所消耗的资源来更好地计费。

>>- 三、IaaS模式
>>>- 作用
通过IaaS这种模式，用户可以从供应商那里获得他所需要的虚拟机或者存储等资源来装载相关的应用，同时这些基础设施的繁琐的管理工作将由IaaS供应商来处理。IaaS能通过它上面对虚拟机支持众多的应用。IaaS主要的用户是系统管理员。
>>>- 产品
主要产品包括：Amazon EC2，Linode，Joyent，Rackspace，IBM Blue Cloud和Cisco UCS等。
>>>- 功能
IaaS供应商需要在那些方面对基础设施进行管理以给用户提供资源?或者说IaaS云有那些功能?在《虚拟化与云计算》中列出了IaaS的七个基本功能：
资源抽象：使用资源抽象的方法(比如，资源池)能更好地调度和管理物理资源。
资源监控：通过对资源的监控，能够保证基础实施高效率的运行。
负载管理：通过负载管理，不仅能使部署在基础设施上的应用运能更好地应对突发情况，而且还能更好地利用系统资源。
数据管理：对云计算而言，数据的完整性，可靠性和可管理性是对IaaS的基本要求。
资源部署：也就是将整个资源从创建到使用的流程自动化。
安全管理：IaaS的安全管理的主要目标是保证基础设施和其提供的资源能被合法地访问和使用。
计费管理：通过细致的计费管理能使用户更灵活地使用资源。
接下来，稍微给大家介绍一下云的三种形式和云计算好处。

>- 三种模式之间的关系
它们之间的关系主要可以从两个角度进行分析：其一是用户体验角度，从这个角度而言，它们之间关系是独立的，因为它们面对不同类型的用户。其二是技术角度，从这个角度而言，它们并不是简单的继承关系(SaaS基于PaaS，而PaaS基于IaaS)，因为首先SaaS可以是基于PaaS或者直接部署于IaaS之上，其次PaaS可以构建于IaaS之上，也可以直接构建在物理资源之上。