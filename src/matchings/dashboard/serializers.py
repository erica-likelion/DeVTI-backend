from rest_framework import serializers


class DashboardFrameworkScoreSerializer(serializers.Serializer):
    team_number = serializers.IntegerField()
    framework_scores = serializers.DictField(child=serializers.FloatField())


class DashboardPartDistSerializer(serializers.Serializer):
    team_number = serializers.IntegerField()
    PM = serializers.IntegerField()
    DE = serializers.IntegerField()
    FE = serializers.IntegerField()
    BE = serializers.IntegerField()


class DashboardPMDesignDistSerializer(serializers.Serializer):
    team_number = serializers.IntegerField()
    pm_design_score = serializers.FloatField(allow_null=True)
    pm_develop_score = serializers.FloatField(allow_null=True)
    design_score = serializers.FloatField(allow_null=True)


class DashboardResponseSerializer(serializers.Serializer):
    part_dist_total = serializers.DictField(child=serializers.IntegerField())
    part_dist = DashboardPartDistSerializer(many=True)
    framework_dist = DashboardFrameworkScoreSerializer(many=True)
    pm_design_dist = DashboardPMDesignDistSerializer(many=True)
