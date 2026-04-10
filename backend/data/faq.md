# AWS 핵심 서비스 가이드 (RAG 테스트용 매뉴얼)

## 1. Amazon EC2 (Elastic Compute Cloud)
### 서비스 개요
Amazon Elastic Compute Cloud(Amazon EC2)는 AWS 클라우드에서 확장 가능 컴퓨팅 용량을 제공합니다. 하드웨어에 선투자할 필요가 없어 애플리케이션을 빠르게 개발하고 배포할 수 있습니다.

### 주요 특징
* **인스턴스 유형:** 컴퓨팅, 메모리, 스토리지 최적화 등 다양한 선택지 제공.
* **확장성:** Auto Scaling을 통해 트래픽에 따라 인스턴스 수를 자동 조절.
* **보안:** 보안 그룹(Security Group)을 통해 네트워크 트래픽 제어.

---

## 2. Amazon S3 (Simple Storage Service)
### 서비스 개요
Amazon S3는 업계 최고의 확장성, 데이터 가용성, 보안 및 성능을 제공하는 객체 스토리지 서비스입니다.

### 데이터 관리 구조
* **버킷(Bucket):** 데이터를 저장하는 기본 컨테이너. 이름은 전역에서 유일해야 합니다.
* **객체(Object):** 데이터 파일과 메타데이터로 구성되며, 최대 5TB까지 저장 가능합니다.
* **스토리지 클래스:** Standard, Intelligent-Tiering, Glacier 등 용도에 따른 비용 최적화 지원.

---

## 3. Amazon RDS (Relational Database Service)
### 서비스 개요
Amazon RDS를 사용하면 클라우드에서 관계형 데이터베이스를 간편하게 설정, 운영 및 확장할 수 있습니다.

### 지원하는 엔진
* Aurora, PostgreSQL, MySQL, MariaDB, Oracle, SQL Server.

### 주요 장점
* **관리형 서비스:** 패치, 백업, 복제 등을 AWS에서 자동으로 처리합니다.
* **고가용성:** Multi-AZ 배포를 통해 데이터베이스 가용성을 극대화합니다.

---

## 4. AWS Lambda (Serverless Computing)
### 서비스 개요
AWS Lambda는 서버를 프로비저닝하거나 관리하지 않고도 코드를 실행할 수 있는 서버리스 컴퓨팅 서비스입니다.

### 작동 방식
1. 사용자가 코드를 업로드하거나 AWS 서비스(S3, DynamoDB 등)에서 트리거를 설정합니다.
2. 이벤트가 발생하면 Lambda가 자동으로 컴퓨팅 자원을 할당하여 코드를 실행합니다.
3. 실행된 시간(밀리초 단위)에 대해서만 비용을 지불합니다.
