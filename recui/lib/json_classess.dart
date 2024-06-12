class MathCenterPage {
  final String name;
  final String uid;
  final String minGrade;
  final String maxGrade;
  final List<dynamic> topics;

  MathCenterPage(
      this.name, this.uid, this.minGrade, this.maxGrade, this.topics);

  MathCenterPage.fromJson(Map<String, dynamic> jsonData)
      : name = jsonData['name'] as String,
        uid = jsonData['uid'] as String,
        minGrade = jsonData['min_grade'] as String,
        maxGrade = jsonData['max_grade'] as String,
        topics = jsonData['topics'] as List<dynamic>;
}
