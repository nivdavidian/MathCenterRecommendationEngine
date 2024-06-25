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

  MathCenterPage.fromRecMathCenterPage(RecMathCenterPage recPage)
      : name = recPage.name,
        uid = recPage.uid,
        minGrade = recPage.minGrade,
        maxGrade = recPage.maxGrade,
        topics = recPage.topics;
}

class RecMathCenterPage {
  final String name;
  final String uid;
  final String minGrade;
  final String maxGrade;
  final List<dynamic> topics;
  final String model;

  RecMathCenterPage(this.name, this.uid, this.minGrade, this.maxGrade,
      this.topics, this.model);

  RecMathCenterPage.fromJson(Map<String, dynamic> jsonData)
      : name = jsonData['name'] as String,
        uid = jsonData['uid'] as String,
        minGrade = jsonData['min_grade'] as String,
        maxGrade = jsonData['max_grade'] as String,
        topics = jsonData['topics'] as List<dynamic>,
        model = jsonData['model'] as String;
}
