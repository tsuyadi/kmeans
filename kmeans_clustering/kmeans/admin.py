from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.db.models import Sum, Count
import numpy as np
import time
import itertools
import pandas as pd
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
from matplotlib.pyplot import cm

from .models import *

admin.site.site_header = 'Clustering KMEANS'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['cif', 'name', 'birth_date', 'account_no', 'card_no']
    search_fields = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account_no', 'channel', 'transaction_type', 'amount', 'transaction_date']
    list_filter = ['channel', 'transaction_type']


@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(TransactionSummary)
class TransactionSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'transaction_summary.html'

    list_filter = ('channel__name',)

    # fungsi untuk inisialisi titik pusat klaster (random)
    def init_centroid(self, data_in, k):
        result = data_in[np.random.choice(data_in.shape[0], k, replace=False)]
        return result

    # fungsi untuk plot hasil klaster per iterasi
    def plotClusterResult(self, listClusterMembers, centroid, iteration, converged):
        n = listClusterMembers.__len__()
        color = iter(cm.rainbow(np.linspace(0, 1, n)))
        plt.figure("result")
        plt.clf()
        plt.title("iteration-" + iteration)
        marker = itertools.cycle(('.', '*', '^', 'x', '+', 'd', 's', 'p'))
        for i in range(n):
            col = next(color)
            memberCluster = np.asmatrix(listClusterMembers[i])
            plt.scatter(np.ravel(memberCluster[:, 0]), np.ravel(memberCluster[:, 1]),
                        marker=next(marker), s=100, c=col, label="klaster-" + str(i + 1))
        for i in range(n):
            plt.scatter((centroid[i, 0]), (centroid[i, 1]), marker=next(marker)
                        , c=col, label="centroid-" + str(i + 1))
        if (converged == 0):
            plt.legend()
            plt.ion()
            plt.show()
            plt.pause(0.1)
        if (converged == 1):
            plt.legend()
            plt.show(block=True)

    # fungsi utama algoritma k-means
    def kMeans(self, data, centroidInit, nCluster, iterationCounter):
        centroidInit = np.matrix(centroidInit)
        # looping hingga konvergen
        while(True):
            iterationCounter += 1
            euclideanMatrixAllCluster = np.ndarray(shape=(data.shape[0], 0))

            print(euclideanMatrixAllCluster)
            # ulangi proses untuk semua klaster
            for i in range(0, nCluster):
                centroidRepeated = np.repeat(centroidInit[i, :], data.shape[0], axis=0)
                deltaMatrix = abs(np.subtract(data, centroidRepeated))
                # hitung jarak Euclidean
                euclideanMatrix = np.sqrt(abs(np.square(deltaMatrix).sum(axis=1)))
                euclideanMatrixAllCluster = \
                    np.concatenate((euclideanMatrixAllCluster, euclideanMatrix), axis=1)
            # tempatkan data ke klaster yang jarak Euclideannya plg dekat
            clusterMatrix = np.ravel(np.argmin(np.matrix(euclideanMatrixAllCluster), axis=1))
            listClusterMember = [[] for i in range(nCluster)]
            for i in range(0, data.shape[0]):  # assign data to cluster regarding cluster matrix
                listClusterMember[np.item(clusterMatrix[i])].append(data[i, :])
            # hitung titik pusat klaster terbaru
            newCentroid = np.ndarray(shape=(0, centroidInit.shape[1]))
            for i in range(0, nCluster):
                memberCluster = np.asmatrix(listClusterMember[i])
                centroidCluster = memberCluster.mean(axis=0)
                newCentroid = np.concatenate((newCentroid, centroidCluster), axis=0)
            print("iter: ", iterationCounter)
            print("centroid: ", newCentroid)
            # break dari loop jika sudah konvergen
            if ((centroidInit == newCentroid).all()):
                break
            # update titik pusat klaster dengan nilai yg baru
            centroidInit = newCentroid
            # plot hasil klaster per iterasi
            self.plotClusterResult(listClusterMember, centroidInit, str(iterationCounter), 0)
            # diberi jeda 1 detik agak hasil plot klaster nyaman dilihat
            time.sleep(1)
        return listClusterMember, centroidInit

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            qs = response.context_data['cl'].queryset

            metrics = {
                'total': Count('id'),
                'total_amount': Sum('amount'),
            }

            response.context_data['summary'] = list(
                qs
                    .values('channel__name')
                    .annotate(**metrics)
                    .order_by('-total_amount')
            )

            response.context_data['summary_total'] = dict(
                qs.aggregate(**metrics)
            )

            vlqs = qs.values_list('account_no_id__birth_date',
                                  'account_no_id', 'account_no_id__cif',
                                  'channel_id', 'transaction_type_id', 'amount')
            data_set = np.matrix(vlqs)

            wcss = []
            # Menemukan jumlah cluster yang optimal untuk klasifikasi k-means
            for i in range(1, 11):
                kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
                kmeans.fit(data_set)
                wcss.append(kmeans.inertia_)

            # Memplot hasilnya ke grafik garis, memungkinkan kita untuk mengamati 'The elbow'
            plt.plot(range(1, 11), wcss)
            plt.title('The elbow method')
            plt.xlabel('Number of clusters')
            plt.ylabel('WCSS')  # within cluster sum of squares
            plt.show()

            # mendefinisikan parameter k-means klustering
            k = 3  # jumlah klaster yg diinginkan
            iteration_counter = 0  # counter untuk iterasi
            data_input = data_set  # input data

            # panggil fungsi inisialisasi klaster
            centroid_init = self.init_centroid(data_input, k)
            # panggil fungsi k-means
            # cluster_results, centroid = self.kMeans(data_input, centroid_init, k, iteration_counter)
            # plot hasil final klaster setelah konvergen
            # self.plotClusterResult(cluster_results, centroid, str(iteration_counter) + " (converged)", 1)

        except (AttributeError, KeyError):
            return response





        return response


# Register your models here.
# admin.site.register(Customer, CustomerAdmin)
# admin.site.register(TransactionType, TransactionTypeAdmin)
# admin.site.register(Channel, ChannelAdmin)
# admin.site.register(Transaction, TransactionAdmin)
admin.site.unregister(Group)
admin.site.unregister(User)
